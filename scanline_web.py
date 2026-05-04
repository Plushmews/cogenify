import random
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
    # 1. Identifier Prefix
    prefix = "99"
    
    # 2. Static '1' and Year '25'
    static_one = "1"
    year = "25"
    
    # 3. Randomized Month (01-12)
    # random.randint(1, 12) picks the month, :02d ensures it is always 2 digits (e.g., "04")
    month = f"{random.randint(1, 12):02d}"
    
    # 4. Two Zeros
    zeros = "00"
    
    # 5. Amount zero-padded to 6 digits
    amount_cents = int(round(amount * 100))
    amount_str = f"{amount_cents:06d}"
    
    # Assemble the base string
    base_string = f"{prefix}{static_one}{year}{month}{zeros}{amount_str}"
    
    # 6. Calculate and append Check Digit
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
        st.subheader(f"Barcode: `{selected_scanline}`")
        
        api_url = "https://bwipjs-api.metafloor.com/"
        
        # 1. Separate the "99" from the rest of the generated string
        internal_data = selected_scanline[2:]
        
        # 2. Configured for a 35x25mm bounding box print
        payload = {
            'bcid': 'databarexpanded',
            'text': f'(99){internal_data}', 
            'alttext': selected_scanline, # Hides the parentheses and prints your raw digits
            'scale': 5,               
            'height': 15,             
            'textfont': 'Helvetica',  
            'textsize': 18,           
            'includetext': '',
            'textyoffset': -8          # <--- NEW: Pushes the text 8 points downward to create a gap!
        }
        
        try:
            with st.spinner("Generating barcode..."):
                response = requests.get(api_url, params=payload)
                
            if response.status_code == 200:
                st.image(response.content, width=350)
            else:
                st.error("Error generating barcode. The API rejected the formatting.")
        except Exception as e:
            st.error("Could not connect to the barcode service.")
