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
