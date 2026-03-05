import streamlit as st
import gspread
from google import genai
from datetime import datetime

# --- 1. SETUP & AUTH ---
st.set_page_config(page_title="Yobo Car Rentals", page_icon="🚗", layout="wide")

# 1. Pull the data from the 'Secrets' tab in Streamlit
    service_account_info = st.secrets["gcp_service_account"]
    
    # 2. Authenticate using the dictionary (NOT a filename)
    gc = gspread.service_account_from_dict(service_account_info)
    
    # 3. Open the sheet
    sh = gc.open("Workshop_Leads") 
    leads_sheet = sh.worksheet("Leads")
    cars_sheet = sh.worksheet("Cars")
    st.sidebar.success("Connected to Sheets!")
except Exception as e:
    st.error(f"Spreadsheet Error: {e}")
    st.stop()
# 2026 Gemini Setup (New SDK)
GEMINI_KEY = "AIzaSyCWHYT0dPymBF_DG5giFXFC6RXTEzRyXNU"
client = genai.Client(api_key=GEMINI_KEY)

# Initialize Session States
if "step" not in st.session_state:
    st.session_state.step = 1
if "user_data" not in st.session_state:
    st.session_state.user_data = {}

# --- 2. THE RENTAL FLOW ---

# STEP 1: GREETING
if st.session_state.step == 1:
    st.subheader("Hello! I'm Yobo. I'm here to assist you in your booking.")
    name = st.text_input("Please tell me your full name:", key="name_input")
    if st.button("Continue") and name:
        st.session_state.user_data['name'] = name
        st.session_state.step = 2
        st.rerun()

# STEP 2: RENTAL DETAILS (Updated with Required Inputs)
elif st.session_state.step == 2:
    name = st.session_state.user_data['name']
    st.subheader(f"Hello {name}, let's get you on the road.")

    with st.form("rental_form"):
        col1, col2 = st.columns(2)
        with col1:
            # Setting 'value=""' as a placeholder, not real data
            phone = st.text_input("Contact Number (Required)")
            email = st.text_input("Gmail (Optional)")  # Email remains optional
            city = st.text_input("City (Required)")
        with col2:
            days = st.number_input("How many days? (Required)", min_value=1, step=1)
            pickup = st.date_input("Pick up date (Required)")
            dropoff = st.date_input("Drop off date (Required)")

        submit_form = st.form_submit_button("Find Available Cars")

        if submit_form:
            # Check for missing required information
            if not phone or not city:
                st.error("⚠️ Please fill in all required fields (Phone and City).")
            else:
                st.session_state.user_data.update({
                    "phone": phone, "email": email, "city": city,
                    "days": days, "pickup": str(pickup), "dropoff": str(dropoff)
                })
                st.session_state.step = 3
                st.rerun()

# STEP 3: CAR SELECTION (Smaller Grid View)
elif st.session_state.step == 3:
    st.subheader("Let's find the perfect model for you")

    cars_data = cars_sheet.get_all_records()
    available_cars = [c for c in cars_data if str(c['Available']).upper() == 'Y']

    if not available_cars:
        st.warning("No cars available. Check your 'Cars' sheet 'Available' column.")
    else:
        # Step A: Increased to 3 columns to shrink image width automatically
        cols = st.columns(3)

        for i, car in enumerate(available_cars):
            # Step B: Placing cards in the 3-column grid
            with cols[i % 3]:
                # Step C: Added border=True for a modern card look
                with st.container(border=True):
                    # Step D: Removed full width, used 'small' width to control size
                    st.image(car['Photo'], width=200)

                    # Step E: Smaller headers (H4) and descriptive labels
                    st.markdown(f"#### {car['Make']} {car['Model']}")

                    # Step F: Small gray text for details to match screenshot style
                    st.caption(f"**Details:** {car['Details']}")
                    st.caption(f"**Color:** {car['Colour']}")
                    st.markdown(f"**Rent:** ₹{car['PricePerDay']}/day")

                    if st.button(f"Choose {car['Model']}", key=f"sel_{i}", use_container_width=True):
                        st.session_state.user_data['selected_car'] = car
                        st.session_state.step = 4
                        st.rerun()

# STEP 4: QUOTE & CONFIRM
elif st.session_state.step == 4:
    car = st.session_state.user_data['selected_car']
    user = st.session_state.user_data
    total_price = int(car['PricePerDay']) * int(user['days'])

    st.success(f"Perfect! Your car is available and ready for pick up on {user['pickup']}.")
    st.metric("Estimated Total Quote", f"₹{total_price}")
    st.info("One of our consultants will call you within the next 2 days to confirm your booking.")

    if st.button("Finalize Booking"):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        leads_sheet.append_row([
            timestamp, user['name'], user['phone'], user['email'],
            user['days'], user['pickup'], user['dropoff'], user['city'],
            f"{car['Make']} {car['Model']}", total_price, "Confirmed"
        ])
        st.balloons()
        st.write("Booking Complete! You can close this window.")
