import random
import streamlit as st
import requests
from PIL import Image, ImageDraw, ImageFont # Handle the "stamping"
import io

# --- Core Algorithm ---
def calculate_check_digit(base_string):
    total = 0
    for i, digit_char in enumerate(reversed(base_string)):
        weight = 3 if i % 2 == 0 else 1
        total += int(digit_char) * weight
    check_digit = (10 - (total % 10)) % 10
    return str(check_digit)

def generate_payment_scanline(amount):
    prefix = "99"
    static_one = "1"
    year = "25"
    month = f"{random.randint(1, 12):02d}"
    zeros = "00"
    amount_cents = int(round(amount * 100))
    amount_str = f"{amount_cents:06d}"
    base_string = f"{prefix}{static_one}{year}{month}{zeros}{amount_str}"
    check_digit = calculate_check_digit(base_string)
    return f"{base_string}{check_digit}"

# --- Web Interface ---
st.set_page_config(page_title="Auto Scanline Generator", page_icon="🖨️")

st.markdown("""
    <style>
        img { border-radius: 0px !important; }
    </style>
""", unsafe_allow_html=True)

st.title("Auto Scanline & Barcode Generator")

if 'saved_scanlines' not in st.session_state:
    st.session_state.saved_scanlines = []

if st.button("Generate 10 Scanlines", type="primary"):
    st.session_state.saved_scanlines = [] 
    for _ in range(10):
        random_amount = random.uniform(500.00, 1250.00)
        scanline = generate_payment_scanline(random_amount) 
        display_text = f"Amount: ${random_amount:7.2f}  |  Scanline: {scanline}"
        st.session_state.saved_scanlines.append((display_text, scanline))

if st.session_state.saved_scanlines:
    st.divider()
    options = [item[0] for item in st.session_state.saved_scanlines]
    selected_option = st.radio("Select a scanline:", options, index=None)
    
    if selected_option:
        selected_scanline = next(item[1] for item in st.session_state.saved_scanlines if item[0] == selected_option)
        internal_data = selected_scanline[2:]
        
        api_url = "https://bwipjs-api.metafloor.com/"
        
        # 1. We request ONLY the barcode lines
        payload = {
            'bcid': 'databarexpanded',
            'text': f'(99){internal_data}', 
            'scale': 5,               
            'height': 20,             
        
        }
        
        try:
            with st.spinner("Rendering Helvetica Barcode..."):
                response = requests.get(api_url, params=payload)
                
            if response.status_code == 200:
                # --- PILLOW PROCESSING ---
                # Open the barcode as a Python image
                barcode_img = Image.open(io.BytesIO(response.content))
                bw, bh = barcode_img.size
                
                # Create a new white canvas with room for text at the bottom (add 120 pixels)
                canvas = Image.new("RGB", (bw, bh + 120), "white")
                canvas.paste(barcode_img, (0, 0))
                
                draw = ImageDraw.Draw(canvas)
                
                # Load Arial (Standard Helvetica clone on Windows/Mac)
                # If running on Linux/Cloud, you may need to point to a specific .ttf file
                try:
                    font = ImageFont.truetype("arial.ttf", 65) 
                except:
                    font = ImageFont.load_default()
                
                # Calculate text position (Centered)
                text_width = draw.textlength(selected_scanline, font=font)
                x_pos = (bw - text_width) // 2
                y_pos = bh + 20  # This is your "space below" (20 pixels gap)
                
                # Draw the clean Helvetica-style text
                draw.text((x_pos, y_pos), selected_scanline, fill="black", font=font)
                
                # Convert back to bytes to show in Streamlit
                img_byte_arr = io.BytesIO()
                canvas.save(img_byte_arr, format='PNG')
                st.image(img_byte_arr.getvalue(), width=350)
                
                st.caption(f"Scanline: {selected_scanline}")
            else:
                st.error("API Error.")
        except Exception as e:
            st.error(f"Processing Error: {e}")
