import streamlit as st
import gspread
from google import genai
from datetime import datetime

# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Yobo Car Rentals", page_icon="🚗", layout="wide")

# --- 2. THE "CENTERED" CSS ---
st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@800&display=swap');

        /* Background and Global Font */
        .stApp {
            background-color: #0E1117 !important;
            font-family: 'Inter', sans-serif !important;
        }

        /* Center the entire block container vertically */
        .main .block-container {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            height: 80vh; /* Adjusts height to center in the middle of the screen */
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
            width: 100%;
        }

        /* CENTERED PILL INPUT */
        div[data-baseweb="input"], div[data-baseweb="base-input"] {
            background-color: #161B22 !important;
            border-radius: 50px !important;
            border: none !important;
            box-shadow: 0 0 0 2px #A78BFA !important;
            width: 100% !important;
        }
        
        input {
            color: white !important;
            background-color: transparent !important;
            text-align: center !important; /* Centers the typing text too */
        }

        /* BUTTONS */
        .stButton>button {
            border-radius: 50px !important;
            background: linear-gradient(90deg, #A78BFA, #6366F1) !important;
            color: white !important;
            border: none !important;
            font-weight: 800 !important;
            width: 100% !important;
            margin-top: 10px;
        }

        /* CAR CARDS (Only apply centering to forms/greetings, not list) */
        .car-card {
            background-color: white !important;
            border-radius: 20px !important;
            padding: 20px !important;
            margin-bottom: 20px !important;
            display: flex !important;
            align-items: center !important;
            box-shadow: 0 0 0 3px #6366F1 !important;
            text-align: left !important;
        }
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
    st.error("Check Secrets.")
    st.stop()

# --- 4. SESSION STATE ---
if "step" not in st.session_state: st.session_state.step = 1
if "user_data" not in st.session_state: st.session_state.user_data = {}

# --- 5. THE FLOW ---

# STEP 1: GREETING (Now Centered)
if st.session_state.step == 1:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 class='main-header'>Hello! I'm Yobo.</h1>", unsafe_allow_html=True)
        name = st.text_input("", placeholder="Enter your full name...", key="name_input")
        if st.button("Get Started") and name:
            st.session_state.user_data['name'] = name
            st.session_state.step = 2
            st.rerun()

# STEP 2: DETAILS (Now Centered)
elif st.session_state.step == 2:
    col1, col2, col3 = st.columns([1,3,1])
    with col2:
        st.markdown(f"<h1 class='main-header'>Welcome, {st.session_state.user_data['name']}</h1>", unsafe_allow_html=True)
        inner_col1, inner_col2 = st.columns(2)
        with inner_col1:
            phone = st.text_input("Phone Number")
            city = st.text_input("City")
        with inner_col2:
            pickup = st.date_input("Pickup Date")
            days = st.number_input("Days", min_value=1)
        if st.button("Browse Fleet"):
            if phone and city:
                st.session_state.user_data.update({"phone": phone, "city": city, "days": days, "pickup": str(pickup)})
                st.session_state.step = 3
                st.rerun()

# STEP 3: FLEET (Scrollable list, so centering is vertical start)
elif st.session_state.step == 3:
    st.markdown("<h1 class='main-header'>Signature Fleet</h1>", unsafe_allow_html=True)
    cars_data = cars_sheet.get_all_records()
    for i, car in enumerate(cars_data):
        if str(car['Available']).upper() == 'Y':
            st.markdown(f"""
            <div class="car-card">
                <div style="flex:1"><img src="{car['Photo']}" width="100%" style="border-radius:10px;"></div>
                <div style="flex:2; color:black; padding-left:20px;">
                    <h2 style="margin:0;">{car['Make']} {car['Model']}</h2>
                    <p style="margin:5px 0;">{car['Details']}</p>
                    <h3 style="color:#6366F1; margin:0;">₹{car['PricePerDay']}/day</h3>
                </div>
            </div>
            """, unsafe_allow_html=True)
            if st.button(f"Select {car['Model']}", key=f"c_{i}"):
                st.session_state.user_data['selected_car'] = car
                st.session_state.step = 4
                st.rerun()
