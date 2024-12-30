from clarifai_grpc.channel.clarifai_channel import ClarifaiChannel
from clarifai_grpc.grpc.api import resources_pb2, service_pb2, service_pb2_grpc
from clarifai_grpc.grpc.api.status import status_code_pb2
import streamlit as st
from gtts import gTTS
from langdetect import detect
from googletrans import Translator
import time
import requests.exceptions
import socket
import ssl
import re

# Constants
USER_ID = 'jvqrpit5yo8j'
PAT = 'da6c272af9f345cb8945fcc48d3a9da5'
APP_ID = 'my-first-application-vr48qs'
WORKFLOW_ID = 'workflow-d9626d'

# Language codes mapping
LANGUAGE_CODES = {
    "English": "en",
    "Hindi": "hi",
    "Tamil": "ta",
    "Telugu": "te",
    "Malayalam": "ml",
    "Kannada": "kn"
}

# Employment and legal keywords for validation
EMPLOYMENT_KEYWORDS = {
    'en': [
        'salary', 'wage', 'pay', 'overtime', 'leave', 'vacation', 'sick', 'maternity',
        'paternity', 'discrimination', 'harassment', 'contract', 'termination', 'fired',
        'redundancy', 'union', 'workplace', 'employment', 'job', 'worker', 'employee',
        'employer', 'work hours', 'benefits', 'compensation', 'retirement', 'pension',
        'resignation', 'notice period', 'severance', 'bonus', 'rights', 'legal', 'law',
        'labour law', 'labor law', 'working conditions', 'shift', 'minimum wage'
    ],
    'hi': [
        'वेतन', 'तनख्वाह', 'पगार', 'ओवरटाइम', 'छुट्टी', 'अवकाश', 'बीमारी', 'मातृत्व',
        'पितृत्व', 'भेदभाव', 'उत्पीड़न', 'अनुबंध', 'नौकरी', 'कर्मचारी', 'मालिक',
        'काम', 'अधिकार', 'कानून', 'श्रम कानून'
    ],
    # Add keywords for other languages as needed
}

def is_employment_related(text, lang='en'):
    """
    Check if the query is related to employment or legal advice
    """
    # Convert text to lowercase for comparison
    text = text.lower()
    
    # Get keywords for the detected language, fallback to English if not available
    keywords = EMPLOYMENT_KEYWORDS.get(lang, EMPLOYMENT_KEYWORDS['en'])
    
    # Check if any employment-related keyword is present in the text
    return any(keyword.lower() in text for keyword in keywords)

def validate_query(text):
    """
    Validate if the query is appropriate for the employment rights chatbot
    """
    # Detect language
    lang = detect_language(text)
    
    # Check if query is employment related
    if not is_employment_related(text, lang):
        return False, "I can only answer questions related to employment rights and legal advice. Please rephrase your question to focus on workplace-related topics."
    
    return True, ""

def get_legal_response(user_query):
    """
    Get legal response after validating the query
    """
    try:
        # Validate query first
        is_valid, error_message = validate_query(user_query)
        if not is_valid:
            return error_message
            
        # Detect input language
        input_lang = detect_language(user_query)
        
        # Translate to English for processing
        translator = Translator()
        english_query = translator.translate(user_query, dest="en").text

        # Get response from Clarifai
        channel = ClarifaiChannel.get_grpc_channel()
        stub = service_pb2_grpc.V2Stub(channel)
        metadata = (('authorization', 'Key ' + PAT),)

        post_workflow_response = stub.PostWorkflowResults(
            service_pb2.PostWorkflowResultsRequest(
                user_app_id=resources_pb2.UserAppIDSet(user_id=USER_ID, app_id=APP_ID),
                workflow_id=WORKFLOW_ID,
                inputs=[
                    resources_pb2.Input(
                        data=resources_pb2.Data(
                            text=resources_pb2.Text(
                                raw=english_query
                            )
                        )
                    )
                ]
            ),
            metadata=metadata
        )

        if post_workflow_response.status.code != status_code_pb2.SUCCESS:
            error_msg = "Error: " + post_workflow_response.status.description
            return retry_translate(error_msg, input_lang)

        # Get English response
        english_response = post_workflow_response.results[0].outputs[-1].data.text.raw
        
        # Additional validation of the response
        if not is_employment_related(english_response):
            return "I apologize, but I can only provide information about employment rights and legal advice. Your question seems to be about a different topic."
        
        # Translate back to input language
        if input_lang != "en":
            return retry_translate(english_response, input_lang)
        return english_response

    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        return retry_translate(error_msg, input_lang)

# [Previous helper functions remain the same]
def detect_language(text):
    """
    Detect the language of the input text
    """
    try:
        lang_code = detect(text)
        lang_mapping = {
            'en': 'en',
            'hi': 'hi',
            'ta': 'ta',
            'te': 'te',
            'ml': 'ml',
            'kn': 'kn'
        }
        return lang_mapping.get(lang_code, 'en')
    except:
        return 'en'

def retry_translate(text, target_lang, max_retries=3, delay=1):
    """
    Retry translation with exponential backoff
    """
    translator = Translator()
    for attempt in range(max_retries):
        try:
            if not text or not target_lang:
                return text
            
            translation = translator.translate(text, dest=target_lang)
            return translation.text
            
        except (requests.exceptions.RequestException, 
                ssl.SSLError, 
                socket.timeout,
                ConnectionError) as e:
            if attempt == max_retries - 1:
                st.warning(f"Translation service temporarily unavailable. Showing original text.")
                return text
            time.sleep(delay * (2 ** attempt))
        except Exception as e:
            st.error(f"Translation error: {str(e)}")
            return text

@st.cache_data(persist=True)
def generate_audio_response(text):
    """
    Generate audio response in detected language
    """
    try:
        lang_code = detect_language(text)
        speech = gTTS(text=text, lang=lang_code, slow=False)
        speech.save("legal_response.mp3")
        return "legal_response.mp3"
    except Exception as e:
        st.error(f"Audio generation error: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Employment Rights and Legal Advice Chatbot",
        layout="wide",
        page_icon="⚖️"
    )

    st.title("Employment Rights and Legal Advice Chatbot")
    
    # Add a disclaimer/information message
    st.info("""
    This chatbot is designed to answer questions specifically about employment rights and legal advice.
    Examples of questions you can ask:
    - What are my rights regarding overtime pay?
    - How much notice period should I get before termination?
    - What are my maternity leave entitlements?
    - How to deal with workplace harassment?
    """)

    # Input type selection
    input_type = st.radio("Choose Input Type", ("Text", "Document Image"))

    if input_type == "Text":
        user_query = st.text_area(
            "Enter your employment-related question:",
            height=100,
            placeholder="Example: What are my rights regarding overtime pay?"
        )

        if st.button("Get Legal Advice"):
            if user_query:
                # First validate the query
                is_valid, error_message = validate_query(user_query)
                
                if not is_valid:
                    st.error(error_message)
                else:
                    with st.spinner("Getting legal advice..."):
                        response = get_legal_response(user_query)

                    st.markdown("### Legal Advice")
                    st.markdown(response)

                    with st.spinner("Generating audio..."):
                        audio_file = generate_audio_response(response)
                        if audio_file:
                            st.audio(audio_file)

                    st.download_button('Download response as text', response, 'legal_advice.txt')
            else:
                st.warning("Please enter a question.")

    else:
        uploaded_file = st.file_uploader("Upload an employment-related document", type=["jpg", "png", "pdf"])

        if uploaded_file:
            st.image(uploaded_file, caption="Uploaded Document", use_column_width=True)

            if st.button("Analyze Document"):
                with st.spinner("Analyzing document..."):
                    file_bytes = uploaded_file.read()
                    # Process image and validate content
                    response = process_image_input(file_bytes)
                
                if response:
                    st.markdown("### Legal Analysis")
                    st.markdown(response)

                    with st.spinner("Generating audio..."):
                        audio_file = generate_audio_response(response)
                        if audio_file:
                            st.audio(audio_file)

                    st.download_button('Download analysis as text', response, 'legal_analysis.txt')

if __name__ == "__main__":
    main()