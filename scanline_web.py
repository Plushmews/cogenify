import random
from datetime import datetime
import streamlit as st
import requests

# --- Core Algorithm ---
def calculate_check_digit(base_string):
    total = 0
    for i, digit_char in enumerate(reversed(base_string)):
        weight = 3 if i % 2 == 0 else 1
        total += int(digit_char) * weight
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)

def generate_payment_scanline(amount):
    prefix = "991"
    current_year = datetime.now().year
    prev_year = str(current_year - 1)[-2:]
    valid_identifiers = ["1100", "1200", "1300", "1400"]
    random_id = random.choice(valid_identifiers)
    
    amount_cents = int(round(amount * 100))
    amount_str = f"{amount_cents:06d}"
    
    base_string = f"{prefix}{prev_year}{random_id}{amount_str}"
    check_digit = calculate_check_digit(base_string)
    
    return f"{base_string}{check_digit}"

# --- Web Interface ---
st.set_page_config(page_title="Auto Scanline Generator", page_icon="🖨️")

st.title("Auto Scanline & Barcode Generator")
st.write("Tap the button below to instantly generate 10 random scanlines.")

# 1. Initialize Session State
if 'saved_scanlines' not in st.session_state:
    st.session_state.saved_scanlines = []

# 2. Generate the Scanlines
if st.button("Generate 10 Scanlines", type="primary"):
    st.session_state.saved_scanlines = [] 
    
    for _ in range(10):
        random_amount = random.uniform(500.00, 1250.00)
        scanline = generate_payment_scanline(random_amount)
        display_text = f"Amount: ${random_amount:7.2f}  |  Scanline: {scanline}"
        st.session_state.saved_scanlines.append((display_text, scanline))

# 3. Display the Clickable List & Barcode
if st.session_state.saved_scanlines:
    st.divider()
    st.subheader("Select a scanline to view its barcode:")
    
    options = [item[0] for item in st.session_state.saved_scanlines]
    selected_option = st.radio("Generated Scanlines:", options, index=None, label_visibility="collapsed")
    
    if selected_option:
        selected_scanline = next(item[1] for item in st.session_state.saved_scanlines if item[0] == selected_option)
        
        st.write("---")
        st.subheader(f"GS1 DataBar Expanded: `{selected_scanline}`")
        
        # Call the BWIP-JS API safely using an encrypted HTTPS connection
        api_url = "https://bwipjs-api.metafloor.com/"
        
      # Adding AI (415) with a 13-digit GLN before the (8020) scanline
        payload = {
            'bcid': 'databarexpanded',
            'text': f'(415)1234567890128(8020){selected_scanline}', 
            'scale': 3,
            'includetext': ''
        }
        
        try:
            with st.spinner("Generating barcode..."):
                # Using 'params' safely handles all the weird URL encoding for the parentheses
                response = requests.get(api_url, params=payload)
                
            if response.status_code == 200:
                st.image(response.content, width=350)
            else:
                st.error(f"Error generating barcode. The API rejected the GS1 formatting.")
        except Exception as e:
            st.error("Could not connect to the barcode service.")
