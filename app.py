import streamlit as st
import google.generativeai as genai
import os
import pytesseract
from PIL import Image
import pandas as pd
from googletrans import Translator
import PyPDF2  # PyMuPDF for reading PDFs
from gtts import gTTS
import tempfile

# Set up Google API key
os.environ["GOOGLE_API_KEY"] = "AIzaSyCwgFhc2NXxnykxGVkzbn8W2y9KkK_M_XM"
genai.configure(api_key=os.environ["GOOGLE_API_KEY"])

# Configure pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Define the Gemini model
model = genai.GenerativeModel("models/gemini-1.5-flash-latest")

# Custom functions
def image_to_text(img):
    extracted_text = pytesseract.image_to_string(img)
    return extracted_text

def pdf_to_text(pdf_file):
    pdf_reader = PyPDF2.PdfReader(pdf_file)
    extracted_text = ""
    for page in pdf_reader.pages:
        extracted_text += page.extract_text()
    return extracted_text

def image_and_query(extracted_text, query):
    response = model.generate_content(f"{query}\n\n{extracted_text}")
    return response.text

def translate_text(text, target_language):
    if not text.strip():
        st.warning("No text provided for translation.")
        return ""
    
    translator = Translator()
    try:
        translated = translator.translate(text, dest=target_language)
        return translated.text
    except Exception as e:
        st.error(f"Translation failed: {e}")
        return ""

def text_to_audio(text, language="en"):
    tts = gTTS(text=text, lang=language)
    temp_audio = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    tts.save(temp_audio.name)
    return temp_audio.name

# Mapping full language names to language codes
language_codes = {
    "English (en)": "en",
    "Spanish (es)": "es",
    "French (fr)": "fr",
    "German (de)": "de",
    "Italian (it)": "it",
    "Portuguese (pt)": "pt",
    "Japanese (ja)": "ja",
    "Korean (ko)": "ko",
    "Hindi (hi)": "hi",
    "Marathi (mr)": "mr"
}

# Streamlit app configuration
st.set_page_config(
    page_title="Image Whisperer",
    page_icon="🖼️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Add custom CSS
# (CSS code omitted for brevity, same as before)

# Sidebar
st.sidebar.header("Explore")
st.sidebar.markdown("""Extract text, generate content, translate, and now hear the audio!""")
st.sidebar.image("img.jpg", use_container_width=True)

# Main layout
st.title("🖼️📄 Image Lex📝")
st.markdown("""Upload an image or PDF, extract details, and listen to the results!""")
st.divider()

# File upload and input
upload_file = st.file_uploader("**Upload an Image or PDF**", type=['png', 'jpg', 'jpeg', 'pdf'])
query = st.text_area("**Craft a story or blog for this file**", placeholder="Type your query here...")

# Radio buttons to choose functionality
option = st.radio(
    "Choose functionality",
    ("Image/PDF to Text", "Content Generation", "Text Translation"),
    index=0
)

# Language selection for translation
if option == "Text Translation":
    target_language = st.selectbox(
        "**Select Language for Translation**", 
        list(language_codes.keys())
    )
    selected_language_code = language_codes.get(target_language)

# Initialize variables for extracted and generated text
extracted_details = ""
generated_details = ""

# Generate button
if st.button("✨ Generate Content"):
    if upload_file and option in ["Image/PDF to Text", "Content Generation", "Text Translation"]:
        with st.spinner("Processing... Please wait!"):
            if upload_file.type.startswith("image/"):
                img = Image.open(upload_file)
                st.image(img, caption="Uploaded Image", use_container_width=True)

                extracted_details = image_to_text(img)
                st.subheader("📄 Extracted Details")
                st.write(extracted_details)

            elif upload_file.type == "application/pdf":
                extracted_details = pdf_to_text(upload_file)
                st.subheader("📄 Extracted Details")
                st.write(extracted_details)

            if option == "Content Generation":
                generated_details = image_and_query(extracted_details, query)
                st.subheader("✨ Generated Details")
                st.write(generated_details)

            if option == "Text Translation":
                # Check if extracted or generated text is available for translation
                if extracted_details.strip():
                    translated_extracted_details = translate_text(extracted_details, selected_language_code)
                    st.subheader("🌍 Translated Extracted Details")
                    st.write(translated_extracted_details)

                if generated_details.strip():
                    translated_generated_details = translate_text(generated_details, selected_language_code)
                    st.subheader("🌍 Translated Generated Details")
                    st.write(translated_generated_details)

            # Text to Audio
            audio_text = generated_details if option == "Content Generation" else extracted_details
            if audio_text.strip():
                audio_file_path = text_to_audio(audio_text)
                st.audio(audio_file_path, format="audio/mp3", start_time=0)

                # Add Download Button for Text File
                st.download_button(
                    label="Download Text",
                    data=audio_text,
                    file_name="text_output.txt",
                    mime="text/plain"
                )

# Footer
st.markdown("""--- Made with ❤️ using Streamlit and Google Generative AI.""")
