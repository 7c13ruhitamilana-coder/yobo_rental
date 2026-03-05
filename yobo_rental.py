import streamlit as st
import gspread
from google import genai
from datetime import datetime

# --- 1. PAGE CONFIG & THEME ---
st.set_page_config(page_title="Yobo Car Rentals", page_icon="🚗", layout="wide")

# CUSTOM CSS FOR NEUE HAAS GROTESK & GRADIENT BORDERS
st.markdown("""
    <style>
        /* Import Neue Haas Grotesk (using Inter as a high-quality fallback if needed) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@700;800&display=swap');

        /* Global Styles */
        .stApp { background-color: #0E1117; color: white; }
        
        /* Heading - Neue Haas Grotesk Style (Inter Bold/ExtraBold) */
        .main-header {
            font-family: 'Inter', 'Helvetica Neue', Helvetica, Arial, sans-serif;
            font-size: 48px;
            font-weight: 800; /* Extra Bold for that Display look */
            letter-spacing: -0.02em; /* Tighter letter spacing like Neue Haas */
            background: -webkit-linear-gradient(#A78BFA, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 30px;
            text-transform: none;
        }

        /* Pill-Shaped Input with Gradient Border */
        div[data-baseweb="input"] {
            border-radius: 50px !important;
            border: 2px solid transparent !important;
            background: linear-gradient(#161B22, #161B22) padding-box,
                        linear-gradient(90deg, #A78BFA 0%, #6366F1 100%) border-box !important;
            padding: 5px 20px;
        }

        /* Car Cards with Gradient Border */
        .car-card-container {
            background-color: white;
            border-radius: 20px;
            padding: 2px; /* This creates the border thickness */
            background: linear-gradient(90deg, #A78BFA 0%, #6366F1 100%);
            margin-bottom: 25px;
        }

        .car-card-content {
            background-color: white;
            border-radius: 18px;
            padding: 20px;
            color: #1A1A1B;
            display: flex;
            align-items: center;
        }
        
        .car-price {
            font-family: 'Inter', sans-serif;
            font-size: 24px;
            font-weight: 700;
            color: #6366F1;
        }

        /* Custom Button */
        .stButton>button {
            border-radius: 50px;
            background: linear-gradient(90deg, #A78BFA 0%, #6366F1 100%);
            color: white;
            border: none;
            padding: 12px 30px;
            font-weight: 700;
            font-family: 'Inter', sans-serif;
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

# STEP 1: GREETING
if st.session_state.step == 1:
    st.markdown("<h1 class='main-header'>Hello! I'm Yobo.</h1>", unsafe_allow_html=True)
    st.write("<p style='text-align:center; color:#8B949E; font-family:sans-serif;'>Type your name below to start your journey.</p>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        name = st.text_input("", placeholder="Enter your full name...", key="name_input")
        st.write(" ") # Spacer
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
        
        st.write(" ")
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
        # Gradient Border Wrapper
        st.markdown(f"""
            <div class="car-card-container">
                <div class="car-card-content">
                    <div style="flex: 1.5;"><img src="{car['Photo']}" style="width:100%; border-radius:10px;"></div>
                    <div style="flex: 2; padding-left: 20px;">
                        <h2 style="margin:0; font-family:'Inter',sans-serif; font-weight:700;">{car['Make']} {car['Model']}</h2>
                        <p style="color:#666; margin:5px 0;">{car['Details']} • {car['Colour']}</p>
                        <p class="car-price">₹{car['PricePerDay']} <span style="font-size:14px; color:#8B949E;">/ day</span></p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button(f"Select {car['Model']}", key=f"btn_{i}", use_container_width=True):
            st.session_state.user_data['selected_car'] = car
            st.session_state.step = 4
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

# STEP 4: FINAL CONFIRMATION
elif st.session_state.step == 4:
    car = st.session_state.user_data['selected_car']
    total = int(car['PricePerDay']) * int(st.session_state.user_state.user_data['days'])
    
    st.markdown("<h1 class='main-header'>Ready to go?</h1>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info(f"Booking: {car['Make']} {car['Model']} for {st.session_state.user_data['days']} days.")
        st.metric("Final Quote", f"₹{total}")
        
        if st.button("Confirm & Finish", use_container_width=True):
            leads_sheet.append_row([
                datetime.now().strftime("%Y-%m-%d"), 
                st.session_state.user_data['name'], 
                st.session_state.user_data['phone'],
                st.session_state.user_data['city'],
                f"{car['Make']} {car['Model']}", 
                total
            ])
            st.success("Booking saved! We will call you shortly.")
