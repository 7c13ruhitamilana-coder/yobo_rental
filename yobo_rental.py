import streamlit as st
import gspread
from google import genai
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Yobo Car Rentals", page_icon="🚗", layout="wide")

# --- 2. THE TYPOGRAPHIC & CENTERED CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;800&display=swap');

        .stApp {
            background-color: #0E1117 !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* NEUE HAAS STYLE HEADING - BOLD */
        .main-header {
            font-family: 'Inter', sans-serif !important;
            font-size: 55px !important;
            font-weight: 800 !important;
            letter-spacing: -0.05em !important;
            background: linear-gradient(90deg, #A78BFA, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 20px;
            width: 100%;
        }

        /* REGULAR WEIGHT FOR TEXT */
        p, span, div, label, .stMarkdown {
            font-family: 'Inter', sans-serif !important;
            font-weight: 400 !important;
        }

        /* Centering Container */
        .main .block-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            min-height: 80vh; 
        }

        /* PILL INPUTS - REGULAR & CENTERED */
        div[data-baseweb="input"], div[data-baseweb="base-input"], div[data-baseweb="calendar"] {
            background-color: #161B22 !important;
            border-radius: 50px !important;
            border: none !important;
            box-shadow: 0 0 0 2px #A78BFA !important;
        }
        
        input {
            color: white !important;
            background-color: transparent !important;
            text-align: center !important;
            font-weight: 400 !important;
        }

        /* BUTTONS - BOLD */
        .stButton>button {
            border-radius: 50px !important;
            background: linear-gradient(90deg, #A78BFA, #6366F1) !important;
            color: white !important;
            border: none !important;
            font-weight: 800 !important;
            width: 100% !important;
        }

        /* CAR CARDS - Button integrated inside */
        .car-card {
            background-color: white !important;
            border-radius: 20px !important;
            padding: 20px !important;
            margin-bottom: 10px !important;
            display: flex !important;
            align-items: center !important;
            box-shadow: 0 0 0 3px #6366F1 !important;
            color: #1A1A1B !important;
        }

        .car-title { font-weight: 800 !important; margin: 0; color: #1A1A1B; }
    </style>
    """, unsafe_allow_html=True)

# --- 3. DATABASE CONNECTION ---
try:
    service_account_info = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(service_account_info)
    sh = gc.open("Workshop_Leads") 
    leads_sheet = sh.worksheet("Leads")
    cars_sheet = sh.worksheet("Cars")
except Exception as e:
    st.error("Database error.")
    st.stop()

# --- 4. SESSION STATE ---
if "step" not in st.session_state: st.session_state.step = 1
if "user_data" not in st.session_state: st.session_state.user_data = {}

# --- 5. THE FLOW ---

# STEP 1: GREETING
if st.session_state.step == 1:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 class='main-header'>Hello! I'm Yobo.</h1>", unsafe_allow_html=True)
        name = st.text_input("", placeholder="Enter your full name...", key="name_input")
        if st.button("Get Started") and name:
            st.session_state.user_data['name'] = name
            st.session_state.step = 2
            st.rerun()

# STEP 2: FULL DETAILS
elif st.session_state.step == 2:
    st.markdown(f"<h1 class='main-header'>Welcome, {st.session_state.user_data['name']}</h1>", unsafe_allow_html=True)
    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            phone = st.text_input("Phone Number")
            email = st.text_input("Gmail (Optional)")
            city = st.text_input("City")
        with c2:
            pickup = st.date_input("Pickup Date")
            dropoff = st.date_input("Drop-off Date")
            days = st.number_input("Total Days", min_value=1)
        
        if st.button("Browse Our Fleet"):
            if phone and city:
                st.session_state.user_data.update({
                    "phone": phone, "email": email, "city": city, 
                    "days": days, "pickup": str(pickup), "dropoff": str(dropoff)
                })
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning("Please provide your phone and city.")

# STEP 3: FLEET SELECTION (Unified Card)
elif st.session_state.step == 3:
    st.markdown("<h1 class='main-header'>Signature Fleet</h1>", unsafe_allow_html=True)
    cars_data = cars_sheet.get_all_records()
    
    for i, car in enumerate(cars_data):
        if str(car['Available']).upper() == 'Y':
            # Card UI
            st.markdown(f"""
            <div class="car-card">
                <div style="flex:1.2"><img src="{car['Photo']}" width="100%" style="border-radius:10px;"></div>
                <div style="flex:2; padding-left:25px;">
                    <h2 class="car-title">{car['Make']} {car['Model']}</h2>
                    <p style="margin:5px 0; color:#4B5563;">{car['Details']} • {car['Colour']}</p>
                    <h3 style="color:#6366F1; margin:0; font-weight:800;">₹{car['PricePerDay']}/day</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Button immediately following card to look connected
            if st.button(f"Book {car['Model']}", key=f"book_{i}"):
                st.session_state.user_data['selected_car'] = car
                st.session_state.step = 4
                st.rerun()
            st.markdown("<div style='margin-bottom:30px;'></div>", unsafe_allow_html=True)

# STEP 4: CONFIRMATION
elif st.session_state.step == 4:
    car = st.session_state.user_data['selected_car']
    user = st.session_state.user_data
    total = int(car['PricePerDay']) * int(user['days'])
    
    st.markdown("<h1 class='main-header'>Ready to go?</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info(f"Booking {car['Make']} {car['Model']} from {user['pickup']} to {user['dropoff']}")
        st.metric("Estimated Total", f"₹{total}")
        if st.button("Confirm & Finish"):
            leads_sheet.append_row([
                datetime.now().strftime("%Y-%m-%d"), user['name'], user['phone'], 
                user['email'], user['city'], f"{car['Make']} {car['Model']}", 
                user['pickup'], user['dropoff'], total
            ])
            st.success("Booking saved! Check your Gmail shortly.")
