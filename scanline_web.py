import random
from datetime import datetime
import streamlit as st

# --- Core Algorithm ---
def calculate_check_digit(base_string):
    total = 0
    # Calculate from right to left, alternating weights of 3 and 1
    for i, digit_char in enumerate(reversed(base_string)):
        weight = 3 if i % 2 == 0 else 1
        total += int(digit_char) * weight
        
    # Find the difference to the next highest multiple of 10
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

st.title("Auto Scanline Generator")
st.write("Tap the button below to instantly generate 10 random scanlines ($500.00 - $1250.00).")

# The button triggers the generation
if st.button("Generate 10 Scanlines", type="primary"):
    results = []
    
    for _ in range(10):
        random_amount = random.uniform(500.00, 1250.00)
        scanline = generate_payment_scanline(random_amount)
        results.append(f"Amount: ${random_amount:7.2f}  |  Scanline: {scanline}")
    
    # Displays the results in a neat, copyable block
    st.code("\n".join(results), language="text")