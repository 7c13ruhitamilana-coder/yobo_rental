import streamlit as st
import gspread
from google import genai
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Yobo Car Rentals", page_icon="🚗", layout="wide")

# --- 2. THE "FORCE" CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@800&display=swap');

        /* Background and Global Font */
        .stApp {
            background-color: #0E1117 !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* NEUE HAAS STYLE HEADING */
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
        }

        /* REMOVE WHITE BOXES & ADD GRADIENT BORDERS TO INPUTS */
        div[data-baseweb="input"], div[data-baseweb="base-input"] {
            background-color: #161B22 !important;
            border-radius: 50px !important;
            border: none !important;
            box-shadow: 0 0 0 2px #A78BFA !important;
        }
        
        input {
            color: white !important;
            background-color: transparent !important;
        }

        /* CAR CARDS WITH GRADIENT GLOW */
        .car-card {
            background-color: white !important;
            border-radius: 20px !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
            display: flex !important;
            align-items: center !important;
            box-shadow: 0 0 0 3px #6366F1 !important;
        }

        /* BUTTONS */
        .stButton>button {
            border-radius: 50px !important;
            background: linear-gradient(90deg, #A78BFA, #6366F1) !important;
            color: white !important;
            border: none !important;
            font-weight: 800 !important;
            width: 100% !important;
            font-family: 'Inter', sans-serif !important;
        }
        
        /* Remove default Streamlit padding */
        .block-container { padding-top: 2rem !important; }
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
    st.error("Check your Streamlit Secrets.")
    st.stop()

# --- 4. SESSION STATE ---
if "step" not in st.session_state: st.session_state.step = 1
if "user_data" not in st.session_state: st.session_state.user_data = {}

# --- 5. THE FLOW ---

# STEP 1: GREETING
if st.session_state.step == 1:
    st.markdown("<h1 class='main-header'>Hello! I'm Yobo.</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input("", placeholder="Enter your full name...", key="name_input")
        if st.button("Get Started") and name:
            st.session_state.user_data['name'] = name
            st.session_state.step = 2
            st.rerun()

# STEP 2: DETAILS
elif st.session_state.step == 2:
    st.markdown(f"<h1 class='main-header'>Welcome, {st.session_state.user_data['name']}</h1>", unsafe_allow_html=True)
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Phone Number")
            city = st.text_input("City")
        with col2:
            pickup = st.date_input("Pickup Date")
            days = st.number_input("Days", min_value=1)
        if st.button("Browse Fleet"):
            if phone and city:
                st.session_state.user_data.update({"phone": phone, "city": city, "days": days, "pickup": str(pickup)})
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning("Please fill in the required details.")

# STEP 3: FLEET SELECTION
elif st.session_state.step == 3:
    st.markdown("<h1 class='main-header'>Signature Fleet</h1>", unsafe_allow_html=True)
    cars_data = cars_sheet.get_all_records()
    available_cars = [c for c in cars_data if str(c['Available']).upper() == 'Y']
    
    for i, car in enumerate(available_cars):
        with st.container():
            st.markdown(f"""
            <div class="car-card">
                <div style="flex:1"><img src="{car['Photo']}" width="100%" style="border-radius:10px;"></div>
                <div style="flex:2; color:black; padding-left:20px;">
                    <h2 style="margin:0; font-family:'Inter', sans-serif;">{car['Make']} {car['Model']}</h2>
                    <p style="margin:5px 0;">{car['Details']} • {car['Colour']}</p>
                    <h3 style="color:#6366F1; margin:0;">₹{car['PricePerDay']}/day</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {car['Model']}", key=f"c_{i}"):
                st.session_state.user_data['selected_car'] = car
                st.session_state.step = 4
                st.rerun()

# STEP 4: FINAL CONFIRMATION
elif st.session_state.step == 4:
    car = st.session_state.user_data['selected_car']
    user = st.session_state.user_data
    total = int(car['PricePerDay']) * int(user['days'])
    
    st.markdown("<h1 class='main-header'>Ready to go?</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info(f"Booking: {car['Make']} {car['Model']} for {user['days']} days.")
        st.metric("Final Quote", f"₹{total}")
        
        if st.button("Confirm & Finish"):
            leads_sheet.append_row([
                datetime.now().strftime("%Y-%m-%d"), 
                user['name'], 
                user['phone'],
                user['city'],
                f"{car['Make']} {car['Model']}", 
                total
            ])
            st.success("Booking saved! We will call you shortly.")
