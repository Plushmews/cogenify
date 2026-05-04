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

# INJECT CUSTOM CSS TO REMOVE STREAMLIT'S ROUNDED EDGES
st.markdown("""
    <style>
        /* Forces all images to have sharp, 90-degree square corners */
        img {
            border-radius: 0px !important;
        }
    </style>
""", unsafe_allow_html=True)

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
        scanline = generate_payment_scanline(
