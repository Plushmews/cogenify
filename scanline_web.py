import random
from datetime import datetime
import streamlit as st
import barcode
from barcode.writer import ImageWriter
from io import BytesIO

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

# 1. Initialize Session State so the lines don't vanish when clicked
if 'saved_scanlines' not in st.session_state:
    st.session_state.saved_scanlines = []

# 2. Generate the Scanlines
if st.button("Generate 10 Scanlines", type="primary"):
    # Clear old results
    st.session_state.saved_scanlines = [] 
    
    for _ in range(10):
        random_amount = random.uniform(500.00, 1250.00)
        scanline = generate_payment_scanline(random_amount)
        # Store both the formatted display text and the raw scanline number
        display_text = f"Amount: ${random_amount:7.2f}  |  Scanline: {scanline}"
        st.session_state.saved_scanlines.append((display_text, scanline))

# 3. Display the Clickable List & Barcode
if st.session_state.saved_scanlines:
    st.divider()
    st.subheader("Select a scanline to view its barcode:")
    
    # Create a clean list of just the display text for the user to click
    options = [item[0] for item in st.session_state.saved_scanlines]
    
    # Use a radio button list for easy selection
    selected_option = st.radio("Generated Scanlines:", options, index=None, label_visibility="collapsed")
    
    if selected_option:
        # Match the clicked text back to the raw 16-digit scanline number
        selected_scanline = next(item[1] for item in st.session_state.saved_scanlines if item[0] == selected_option)
        
        st.write("---")
        st.subheader(f"Barcode for: `{selected_scanline}`")
        
        # Generate the Code 128 Barcode Image
        Code128 = barcode.get_barcode_class('code128')
        my_barcode = Code128(selected_scanline, writer=ImageWriter())
        
        # Save it to a virtual buffer so Streamlit can render it instantly
        buffer = BytesIO()
        my_barcode.write(buffer)
        
        # Display the image on the web page
        st.image(buffer.getvalue(), width=400)
