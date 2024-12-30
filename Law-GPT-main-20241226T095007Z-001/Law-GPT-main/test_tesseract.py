import re
import pytesseract
from PIL import Image
import streamlit as st

def extract_important_points(text):
    """
    Extract key details from offer letter text with flexible pattern matching
    :param text: Extracted text from the image
    :return: Dictionary containing important points
    """
    important_info = {}
    
    patterns = {
        "Employee Name": [
            r"Dear\s+([A-Za-z\s\.]+)",
            r"offered to\s+([A-Za-z\s\.]+)",
            r"offer\s+(?:to|for)\s+([A-Za-z\s\.]+)"
        ],
        "Company Name": [
            r"OFFER LETTER\s*[-]\s*([A-Za-z\s]+(?:TECHNOLOGIES|SOLUTIONS|CORP|LLC|LTD|INC|INTERNATIONAL|ENTERPRISES|SYSTEMS|CONSULTING|CAVE))",
            r"internship\s+with\s+([A-Za-z\s]+(?:Technologies|Solutions|Corp|LLC|Ltd|Inc|International|Enterprises|Systems|Consulting|Cave))",
            r"([A-Z][A-Z\s]+(?:TECHNOLOGIES|SOLUTIONS|CORP|LLC|LTD|INC|INTERNATIONAL|ENTERPRISES|SYSTEMS|CONSULTING|CAVE))",
        ],
        "Position": [
            r"Position:\s*([^,\n]+)",
            r"as\s+(?:an?\s+)?([^,\.\n]+(?:Intern|Developer|Engineer)[^,\.\n]*)",
            r"offer\s+(?:you\s+)?(?:an?\s+)?internship\s+(?:as|for)\s+(?:an?\s+)?([^,\.\n]+)"
        ],
        "Start Date": [
            r"Start Date:\s*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})",
            r"last\s+from\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            r"starting\s+(?:from\s+)?(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            r"period\s+(?:from|of)\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})"
        ],
        "End Date": [
            r"End Date:\s*(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s+\d{4})",
            r"to\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})",
            r"until\s+(\d{1,2}\s+[A-Za-z]+\s+\d{4})"
        ],
        "Duration": [
            r"Duration:\s*([^,\n]+)",
            r"Period:\s*([^,\n]+)",
            r"internship\s+(?:will\s+)?last\s+(?:for\s+)?([^,\.\n]+)",
            r"(\d+(?:\.\d+)?\s+(?:month|week)s?\s+(?:period|duration|internship))"
        ],
        "Internship Type": [
            r"This\s+is\s+(?:an?\s+)?([^,\.\n]+(?:based|training|learning)\s+internship)",
            r"Type:\s*([^,\.\n]+)"
        ],
        "Contact Info": [
            r"(contact@[^\s|]+)",
            r"([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})",
            r"Email:?\s*([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})"
        ],
        "Website": [
            r"Website:?\s*((?:www|http://|https://)[^\s|]+)",
            r"(?:www|http://|https://)[^\s|]+"
        ]
    }

    # Process each field
    for field, pattern_list in patterns.items():
        found = False
        for pattern in pattern_list:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE | re.DOTALL)
            if match:
                try:
                    extracted_text = match.group(1)
                    if extracted_text:
                        # Clean up the extracted text
                        cleaned_text = ' '.join(extracted_text.split())
                        cleaned_text = re.sub(r'^[,\s\.]+|[,\s\.]+$', '', cleaned_text)
                        # Remove any remaining quotes or special characters
                        cleaned_text = re.sub(r'["\']', '', cleaned_text)
                        important_info[field] = cleaned_text
                        found = True
                        break
                except (IndexError, AttributeError):
                    continue
        
        if not found:
            important_info[field] = "Not Found"

    # Additional post-processing for specific fields
    if important_info["Position"] != "Not Found":
        if "intern" in important_info["Position"].lower():
            position_parts = important_info["Position"].split("Intern")
            if len(position_parts) > 1:
                important_info["Position"] = position_parts[0].strip() + " Intern"

    return important_info

# Streamlit app UI
def main():
    st.title("Offer Letter Information Extractor")
    st.write("Upload an image of an offer letter, and the key details will be extracted.")

    # File uploader
    uploaded_file = st.file_uploader("Choose an image", type=["jpg", "png", "jpeg"])
    
    if uploaded_file is not None:
        # Open image and extract text using Tesseract
        image = Image.open(uploaded_file)
        
        # Add image preprocessing options
        st.sidebar.subheader("Image Preprocessing Options")
        resize_factor = st.sidebar.slider("Resize Factor", 1.0, 3.0, 2.0, 0.1)
        
        # Resize image for better OCR
        width, height = image.size
        new_size = (int(width * resize_factor), int(height * resize_factor))
        image = image.resize(new_size, Image.Resampling.LANCZOS)
        
        # Extract text
        extracted_text = pytesseract.image_to_string(image)
        
        # Display the image
        st.subheader("Uploaded Image")
        st.image(image, use_container_width=True)
        
        # Extract and display information
        important_info = extract_important_points(extracted_text)
        
        # Display results in a more organized way
        st.subheader("Extracted Information")
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Basic Details**")
            st.write(f"📝 Employee Name: {important_info['Employee Name']}")
            st.write(f"🏢 Company Name: {important_info['Company Name']}")
            st.write(f"💼 Position: {important_info['Position']}")
            st.write(f"🔄 Internship Type: {important_info['Internship Type']}")
            st.write(f"⏱️ Duration: {important_info['Duration']}")
        
        with col2:
            st.markdown("**Dates and Contact**")
            st.write(f"📅 Start Date: {important_info['Start Date']}")
            st.write(f"🔚 End Date: {important_info['End Date']}")
            st.write(f"📧 Contact Info: {important_info['Contact Info']}")
            st.write(f"🌐 Website: {important_info['Website']}")
        
        # Option to view raw extracted text
        if st.checkbox("Show Raw Extracted Text"):
            st.subheader("Raw Extracted Text")
            st.text(extracted_text)

if __name__ == "__main__":
    main()