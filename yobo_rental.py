import streamlit as st
import gspread
from google import genai
from datetime import datetime
import streamlit as st

# 1. FORCED CSS: FONT & OMBRE RECOVERY
st.markdown("""
    <style>
    /* Force font to Neue Haas Grotesk */
    @import url('https://fonts.cdnfonts.com/css/neue-haas-grotesk-display');
    
    html, body, [class*="st-"], .stMarkdown, .stButton>button {
        font-family: 'Neue Haas Grotesk Display', 'Helvetica Neue', Helvetica, sans-serif !important;
    }

    /* Force the Ombre background to stay fixed */
    .stApp {
        background: linear-gradient(135deg, #fbc2eb 0%, #a6c1ee 100%) !important;
        background-attachment: fixed;
    }

    /* Styling for the attached button look */
    .stButton > button {
        border-radius: 5px;
        height: 3em;
    }
    </style>
""", unsafe_allow_html=True)

# 2. CAR SECTION: ATTACHING THE BOOK BUTTON
st.title("Yobo Rental")

# Creating a card for the Supra
with st.container():
    st.subheader("Toyota Supra MK5")
    
    # We use columns with gap="none" or "small" to 'attach' the button to the input
    col_input, col_btn = st.columns([3, 1], gap="small")
    
    with col_input:
        # This acts as the anchor for the button
        st.text_input("Selected Car", value="Supra MK5", label_visibility="collapsed", disabled=True)
    
    with col_btn:
        # Attached button
        if st.button("Book Supra", use_container_width=True):
            st.success("Redirecting to booking...")

# --- Space between sections ---
st.divider()

# 3. CHAT & NAVIGATION: KEEPING BUTTONS SEPARATE
# Chat bar first
chat_input = st.chat_input("Ask about our fleet...")

# Significant vertical spacing to keep Get Started separated
st.write("##") 
st.write("##")

# Get Started button at the bottom
with st.container():
    if st.button("Get Started", type="primary", use_container_width=True):
        st.info("Let's set up your profile!")
# --- 1. PAGE CONFIG ---
st.set_page_config(page_title="Yobo Car Rentals", page_icon="🚗", layout="wide")

# --- 2. TYPOGRAPHY & CSS ---
st.markdown("""
    <style>
        /* Targeting Neue Haas Grotesk Display */
        html, body, [class*="st-"] {
            font-family: "Neue Haas Grotesk Display", "Helvetica Neue", Helvetica, Arial, sans-serif !important;
        }

        .main-header {
            font-size: 55px !important;
            font-weight: 700 !important; /* Bold */
            letter-spacing: -0.05em !important;
            background: linear-gradient(90deg, #A78BFA, #6366F1);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 20px;
        }

        /* Regular weight for body text */
        p, span, div, label {
            font-weight: 400 !important;
        }

        /* Compact Car Card */
        .car-card {
            background-color: white !important;
            border-radius: 20px 20px 0 0 !important; /* Flat bottom to join button */
            padding: 15px !important;
            display: flex !important;
            align-items: center !important;
            border: 2px solid #6366F1 !important;
            border-bottom: none !important;
            color: #1A1A1B !important;
        }

        /* Integrated Button */
        .stButton>button {
            border-radius: 0 0 20px 20px !important; /* Rounded bottom only */
            background: linear-gradient(90deg, #A78BFA, #6366F1) !important;
            color: white !important;
            border: none !important;
            font-weight: 700 !important;
            width: 100% !important;
            margin-top: -2px !important; /* Overlap border */
        }

        .car-title { font-weight: 700 !important; margin: 0; color: #1A1A1B; font-size: 1.2rem; }
        
        /* Pill Inputs */
        div[data-baseweb="input"] {
            border-radius: 50px !important;
            background-color: #161B22 !important;
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
    st.error("Database error.")
    st.stop()

if "step" not in st.session_state: st.session_state.step = 1
if "user_data" not in st.session_state: st.session_state.user_data = {}

# --- 4. THE FLOW ---

if st.session_state.step == 1:
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.markdown("<h1 class='main-header'>Hello! I'm Yobo.</h1>", unsafe_allow_html=True)
        name = st.text_input("", placeholder="Enter your full name...", key="name_input")
        if st.button("Get Started") and name:
            st.session_state.user_data['name'] = name
            st.session_state.step = 2
            st.rerun()

elif st.session_state.step == 2:
    st.markdown(f"<h1 class='main-header'>Welcome, {st.session_state.user_data['name']}</h1>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        phone = st.text_input("Phone Number")
        email = st.text_input("Email")
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

elif st.session_state.step == 3:
    st.markdown("<h1 class='main-header'>Signature Fleet</h1>", unsafe_allow_html=True)
    cars_data = cars_sheet.get_all_records()
    
    # Center the fleet display
    _, central_col, _ = st.columns([1, 2, 1])
    
    with central_col:
        for i, car in enumerate(cars_data):
            if str(car['Available']).upper() == 'Y':
                st.markdown(f"""
                <div class="car-card">
                    <div style="flex:1"><img src="{car['Photo']}" width="100%" style="border-radius:10px;"></div>
                    <div style="flex:2; padding-left:20px;">
                        <h2 class="car-title">{car['Make']} {car['Model']}</h2>
                        <p style="margin:2px 0; color:#4B5563; font-size:0.9rem;">{car['Details']}</p>
                        <h3 style="color:#6366F1; margin:0; font-weight:700;">₹{car['PricePerDay']}/day</h3>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"Book {car['Model']}", key=f"book_{i}"):
                    st.session_state.user_data['selected_car'] = car
                    st.session_state.step = 4
                    st.rerun()
                st.markdown("<br>", unsafe_allow_html=True)

elif st.session_state.step == 4:
    car = st.session_state.user_data['selected_car']
    user = st.session_state.user_data
    total = int(car['PricePerDay']) * int(user['days'])
    
    st.markdown("<h1 class='main-header'>Ready to go?</h1>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.info(f"Booking {car['Make']} {car['Model']} in {user['city']}")
        st.metric("Estimated Total", f"₹{total}")
        if st.button("Confirm & Finish"):
            # MATCHING THE COLUMN ORDER: 
            # Timestamp, Name, Phone, Email, Days, Pickup, Drop off, City, Car, Quote, Status
            leads_sheet.append_row([
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 
                user['name'], 
                user['phone'], 
                user['email'], 
                user['days'], 
                user['pickup'], 
                user['dropoff'], 
                user['city'], 
                f"{car['Make']} {car['Model']}", 
                total, 
                "Confirmed"
            ])
            st.success("Booking saved! See you soon.")
