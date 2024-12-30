import pytesseract
from PIL import Image
import io
import streamlit as st

# Correctly set the Tesseract executable path
pytesseract.pytesseract.tesseract_cmd = r"C:\Users\Shankar\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image_bytes):
    """Extract text from image using Tesseract OCR."""
    try:
        # Convert the bytes data into a PIL Image
        image = Image.open(io.BytesIO(image_bytes))
        
        # Use Tesseract to extract text from the image
        text = pytesseract.image_to_string(image)
        return text
    except Exception as e:
        return f"Error extracting text: {e}"

# Streamlit setup
st.set_page_config(page_title="Image to Text using Tesseract", layout="wide")

st.title("Image to Text OCR")

# File uploader for image input
uploaded_file = st.file_uploader("Upload an image file", type=["jpg", "png", "jpeg", "bmp", "gif"])

if uploaded_file is not None:
    # Read image file as bytes
    image_bytes = uploaded_file.read()

    # Display the image
    st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
    
    # Extract text from the image
    with st.spinner("Extracting text..."):
        extracted_text = extract_text_from_image(image_bytes)
        
    st.subheader("Extracted Text:")
    st.text_area("Text extracted from image:", extracted_text, height=300)

    # Optionally, allow users to download the text
    st.download_button(
        label="Download Extracted Text",
        data=extracted_text,
        file_name="extracted_text.txt",
        mime="text/plain"
    )
