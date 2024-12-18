import streamlit as st
import google.generativeai as genai
import os
import pytesseract
from PIL import Image
import pandas as pd
from googletrans import Translator

# Set up Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCwgFhc2NXxnykxGVkzbn8W2y9KkK_M_XM"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the Gemini model
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Custom functions
def image_to_text(img):
    # Use Tesseract OCR to extract text from the image
    extracted_text = pytesseract.image_to_string(img)
    return extracted_text

def image_and_query(extracted_text, query):
    # Combine the extracted text with the user's query for the Gemini model
    response = model.generate_content(f"{query}\n\n{extracted_text}")
    return response.text

def translate_text(text, target_language):
    # Translate text using googletrans
    translator = Translator()
    try:
        # Translate the text using googletrans
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return ""

# Mapping full language names to language codes
language_codes = {
    "English (en)": "en",
    "Spanish (es)": "es",
    "French (fr)": "fr",
    "German (de)": "de",
    "Italian (it)": "it",
    "Portuguese (pt)": "pt",
    "Japanese (ja)": "ja",
    "Korean (ko)": "ko"
}

# Streamlit app configuration
st.set_page_config(
    page_title="Image Whisperer",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS for background animation and general styling
st.markdown("""
    <style>
    /* Apply background animation */
    @keyframes backgroundAnimation {
        0% { background-color: #FFEBB7; }
        50% { background-color: #FFDFB1; }
        100% { background-color: #FFEBB7; }
    }
    
    .reportview-container {
        animation: backgroundAnimation 10s ease-in-out infinite;
        color: #333333;  /* Dark text for better readability */
    }
    
    /* Sidebar custom background color */
    .sidebar .sidebar-content {
        background-color: #FFDFB1; /* Lighter yellow for sidebar */
        color: #333333;
        border-radius: 10px;
        padding: 20px;
    }
    
    /* Header Styling */
    h1 {
        color: #D94F4F; /* Deep Red color for the title */
        font-size: 40px;
        font-weight: bold;
    }

    /* Button Styling (Updated to Light Blue) */
    .stButton>button {
        background-color: #ADD8E6; /* Light Blue Button */
        color: #333333;
        border-radius: 10px;
        padding: 10px 20px;
        font-size: 16px;
        transition: background-color 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #87CEEB; /* Darker Blue on hover */
    }
    
    /* Input Text Area Styling (Darker Background for Textboxes) */
    .stTextInput input, .stTextArea textarea {
        background-color: #3F3F3F; /* Dark background for inputs */
        color: #FFFFFF; /* White text for contrast */
        border: 2px solid #444444; /* Darker border */
        padding: 12px;
        border-radius: 10px;
    }
    
    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: #FF6347; /* Tomato Red Border on Focus */
    }
    
    /* File Upload Background Styling */
    .stFileUploader>div {
        background-color: #FFFAF0; /* Light Cream for file upload section */
        color: #333333;
        border-radius: 10px;
    }

    /* Footer Styling */
    footer {
        text-align: center;
        padding: 20px;
        background-color: #FFEBB7; /* Light Yellow for footer */
        color: #333333;
    }
    
    .stDownloadButton>button {
        background-color: #ADD8E6; /* light bluefor download button */
        color: white;
        border-radius: 10px;
        padding: 12px 20px;
        font-size: 14px;
    }
    
    .stButton>button:hover {
        background-color: #87CEEB; /* Darker Blue on hover */
    }
    </style>
""", unsafe_allow_html=True)


# Sidebar
st.sidebar.header("Explore")
st.sidebar.markdown(
    """
    Use this app to:
    - Extract text from images using OCR
    - Generate content based on image details
    - Translate extracted/generated content to another language
    """
)
st.sidebar.image("C:\ImagetoText\its an image to text generator which inamed as image whisperer.jpg", use_container_width=True)

# Main layout
st.title("🖼️ Image Whisperer📝")
st.markdown(
    """
    Upload an image, extract text details, generate a story or blog post based on your query, and even translate the content to another language.
    """
)
st.divider()

# File upload and input
upload_image = st.file_uploader("**Upload an Image**", type=['png', 'jpg', 'jpeg'])
query = st.text_area("**Craft a story or blog for this image**", placeholder="Type your query here...")

# Radio buttons to choose functionality
option = st.radio(
    "Choose functionality",
    ("Image to Text", "Content Generation", "Text Translation"),
    index=0
)

# Language selection for translation
if option == "Text Translation":
    target_language = st.selectbox(
        "**Select Language for Translation**", 
        ["English (en)", "Spanish (es)", "French (fr)", "German (de)", "Italian (it)", 
         "Portuguese (pt)", "Japanese (ja)", "Korean (ko)"]
    )
    # Get the language code from the selected full name
    selected_language_code = language_codes.get(target_language)

# Define variables for generated and extracted details
extracted_details = ""
generated_details = ""

# Generate button
if st.button("✨ Generate Content"):
    if upload_image and (option == "Image to Text" or option == "Content Generation" or option == "Text Translation"):
        with st.spinner("Processing... Please wait!"):
            img = Image.open(upload_image)
            st.image(img, caption="Uploaded Image", use_container_width=True)

            # Image to Text
            if option == "Image to Text":
                extracted_details = image_to_text(img)
                st.subheader("📄 Extracted Details")
                if extracted_details.strip():
                    st.success("Text extracted successfully!")
                    st.write(extracted_details)
                else:
                    st.error("No text detected in the image. Please try another image.")

            # Content Generation
            if option == "Content Generation":
                extracted_details = image_to_text(img)
                generated_details = image_and_query(extracted_details, query)
                st.subheader("✨ Generated Details")
                st.write(generated_details)

            # Text Translation
            if option == "Text Translation" and selected_language_code:
                extracted_details = image_to_text(img)
                generated_details = image_and_query(extracted_details, query)
                
                translated_extracted_details = translate_text(extracted_details, selected_language_code)
                translated_generated_details = translate_text(generated_details, selected_language_code)

                st.subheader("🌍 Translated Extracted Details")
                st.write(translated_extracted_details)

                st.subheader("🌍 Translated Generated Details")
                st.write(translated_generated_details)

            # Save to CSV
            data = {"Extracted Details": [extracted_details], "Generated Details": [generated_details]}
            df = pd.DataFrame(data)
            csv = df.to_csv(index=False)

            st.download_button(
                label="Download Results as CSV",
                data=csv,
                file_name="details.csv",
                mime="text/csv"
            )
    else:
        st.error("Please upload an image and provide a query.")

# Footer
st.markdown(
    """
    ---
    Made with ❤️ using [Streamlit](https://streamlit.io/) and Google Generative AI.
    """
)
