import streamlit as st
import gspread
from google import genai
from datetime import datetime

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="Yobo Car Rentals", page_icon="🚗", layout="wide")

# INTERNAL CSS FOR THE "AI ASSISTANT" & "MENU GRID" LOOK
st.markdown("""
    <style>
        /* Global Styles */
        .stApp { background-color: #0E1117; color: white; }
        
        /* Heading Gradient - Match Sample 1 */
        .main-header {
            font-size: 45px;
            font-weight: 800;
            background: -webkit-linear-gradient(#A78BFA, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 30px;
        }

        /* Pill-Shaped Input - Match Sample 2 */
        div[data-baseweb="input"] {
            border-radius: 50px !important;
            border: 1px solid #30363D !important;
            background-color: #161B22 !important;
            padding: 5px 20px;
        }

        /* Car Cards - Match Sample 3 (Menu Style) */
        .car-card {
            background-color: white;
            border-radius: 20px;
            padding: 20px;
            margin-bottom: 20px;
            color: #1A1A1B;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5);
            display: flex;
            align-items: center;
            border-left: 8px solid #6366F1; /* Accent Line */
        }
        
        .car-price {
            font-size: 24px;
            font-weight: bold;
            color: #6366F1;
        }

        /* Custom Button */
        .stButton>button {
            border-radius: 50px;
            background: linear-gradient(90deg, #A78BFA 0%, #6366F1 100%);
            color: white;
            border: none;
            padding: 10px 25px;
            font-weight: bold;
        }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATABASE CONNECTION ---
try:
    service_account_info = st.secrets["gcp_service_account"]
    gc = gspread.service_account_from_dict(service_account_info)
    sh = gc.open("Workshop_Leads") 
    leads_sheet = sh.worksheet("Leads")
    cars_sheet = sh.worksheet("Cars")
except Exception as e:
    st.error("Connection Error. Please check your Secrets.")
    st.stop()

# --- 3. SESSION STATE ---
if "step" not in st.session_state: st.session_state.step = 1
if "user_data" not in st.session_state: st.session_state.user_data = {}

# --- 4. THE FLOW ---

# STEP 1: GREETING (AI STYLE)
if st.session_state.step == 1:
    st.markdown("<h1 class='main-header'>Hello! I'm Yobo.</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; color:#8B949E;'>Type your name below to start your journey.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input("", placeholder="Enter your full name...", key="name_input")
        if st.button("Get Started", use_container_width=True) and name:
            st.session_state.user_data['name'] = name
            st.session_state.step = 2
            st.rerun()

# STEP 2: DETAILS FORM
elif st.session_state.step == 2:
    st.markdown(f"<h1 class='main-header'>Welcome, {st.session_state.user_data['name']}</h1>", unsafe_allow_html=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            phone = st.text_input("Contact Number")
            city = st.text_input("Your City")
        with col2:
            pickup = st.date_input("Pick up date")
            days = st.number_input("Duration (Days)", min_value=1)
        
        if st.button("Browse Our Fleet", use_container_width=True):
            if phone and city:
                st.session_state.user_data.update({"phone": phone, "city": city, "days": days, "pickup": str(pickup)})
                st.session_state.step = 3
                st.rerun()
            else:
                st.warning("Please fill in the required details.")

# STEP 3: THE MENU GRID (CAR SELECTION)
elif st.session_state.step == 3:
    st.markdown("<h1 class='main-header'>Our Signature Fleet</h1>", unsafe_allow_html=True)
    
    cars_data = cars_sheet.get_all_records()
    available_cars = [c for c in cars_data if str(c['Available']).upper() == 'Y']

    for i, car in enumerate(available_cars):
        # Create a "Menu Item" card for each car
        with st.container():
            col_img, col_txt, col_btn = st.columns([1.5, 2, 1])
            
            with col_img:
                st.image(car['Photo'], use_container_width=True)
            
            with col_txt:
                st.markdown(f"<h2 style='color:white; margin:0;'>{car['Make']} {car['Model']}</h2>", unsafe_allow_html=True)
                st.markdown(f"<p style='color:#8B949E;'>{car['Details']} • {car['Colour']}</p>", unsafe_allow_html=True)
                st.markdown(f"<p class='car-price'>₹{car['PricePerDay']} <span style='font-size:14px; color:#8B949E;'>/ day</span></p>", unsafe_allow_html=True)
            
            with col_btn:
                st.write(" ") # Spacer
                if st.button(f"Select Model", key=f"btn_{i}", use_container_width=True):
                    st.session_state.user_data['selected_car'] = car
                    st.session_state.step = 4
                    st.rerun()
        st.markdown("<hr style='border:0.1px solid #30363D;'>", unsafe_allow_html=True)

# STEP 4: FINAL CONFIRMATION
elif st.session_state.step == 4:
    car = st.session_state.user_data['selected_car']
    total = int(car['PricePerDay']) * int(st.session_state.user_data['days'])
    
    st.markdown("<h1 class='main-header'>Ready to go?</h1>", unsafe_allow_html=True)
    st.balloons()
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info(f"Booking: {car['Make']} {car['Model']} for {st.session_state.user_data['days']} days.")
        st.metric("Final Quote", f"₹{total}")
        
        if st.button("Confirm & Finish", use_container_width=True):
            # Save to Sheets
            leads_sheet.append_row([
                datetime.now().strftime("%Y-%m-%d"), 
                st.session_state.user_data['name'], 
                st.session_state.user_data['phone'],
                st.session_state.user_data['city'],
                f"{car['Make']} {car['Model']}", 
                total
            ])
            st.success("Booking saved! We will call you shortly.")
