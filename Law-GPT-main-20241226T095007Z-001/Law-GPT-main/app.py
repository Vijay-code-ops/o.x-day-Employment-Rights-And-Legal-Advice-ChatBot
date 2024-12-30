import streamlit as st
from gtts import gTTS
from workflow_text_to_text import get_legal_response
import pytesseract
from PIL import Image
import io
import speech_recognition as sr
import tempfile
import sounddevice as sd
import soundfile as sf
import numpy as np
import datetime
import json
import os

# File to store chat history
HISTORY_FILE = "chat_history.json"

def load_chat_history():
    """
    Load chat history from file
    """
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(f"Error loading chat history: {e}")
    return []

def save_chat_history(history):
    """
    Save chat history to file
    """
    try:
        with open(HISTORY_FILE, 'w') as f:
            json.dump(history, f)
    except Exception as e:
        print(f"Error saving chat history: {e}")

# Initialize session state for chat history and messages
if 'chat_history' not in st.session_state:
    st.session_state['chat_history'] = load_chat_history()
if 'messages' not in st.session_state:
    st.session_state['messages'] = []

# Cache the audio generation function
@st.cache_data(persist=True)
def generate_audio_response(text):
    """
    Generate an audio response using gTTS.
    :param text: Text to be converted into speech.
    :return: Path to the generated audio file.
    """
    speech = gTTS(text=text, lang='en', slow=False)
    speech.save("legal_response.mp3")
    return "legal_response.mp3"

def record_audio(duration=5):
    """
    Record audio from the microphone.
    :param duration: Recording duration in seconds
    :return: Path to the recorded audio file
    """
    sample_rate = 44100
    recording = sd.rec(int(duration * sample_rate), 
                      samplerate=sample_rate, 
                      channels=1, 
                      dtype=np.float32)
    sd.wait()
    
    temp_file = tempfile.mktemp(suffix='.wav')
    sf.write(temp_file, recording, sample_rate)
    return temp_file

def speech_to_text(audio_file):
    """
    Convert speech to text using speech recognition.
    :param audio_file: Path to the audio file
    :return: Transcribed text
    """
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file) as source:
        audio = recognizer.record(source)
    try:
        return recognizer.recognize_google(audio)
    except sr.UnknownValueError:
        return "Speech could not be understood"
    except sr.RequestError:
        return "Could not request results from speech recognition service"

def add_to_chat_history(question, answer):
    """
    Add a Q&A pair to the chat history with timestamp and save to file
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_chat = {
        "timestamp": timestamp,
        "question": question,
        "answer": answer
    }
    st.session_state['chat_history'].append(new_chat)
    # Save to file
    save_chat_history(st.session_state['chat_history'])
    # Also add to messages for display
    st.session_state['messages'].append({"role": "user", "content": question})
    st.session_state['messages'].append({"role": "assistant", "content": answer})

# Streamlit page configuration
st.set_page_config(
    page_title="Employment Rights and Legal Advice Chatbot",
    layout="wide",
    page_icon="⚖"
)

# Create two columns: one for chat history (smaller) and one for main content (larger)
col1, col2 = st.columns([1, 3])

# Chat History Sidebar (Column 1)
with col1:
    st.title("Chat History")
    
    # Clear history button with confirmation
    if st.button("Clear History"):
        if st.button("Confirm Clear History"):
            st.session_state['chat_history'] = []
            st.session_state['messages'] = []
            # Remove the history file
            if os.path.exists(HISTORY_FILE):
                os.remove(HISTORY_FILE)
            st.rerun()
    
    # Display chat history
    for i, chat in enumerate(reversed(st.session_state['chat_history'])):
        with st.expander(f"Chat {len(st.session_state['chat_history'])-i} - {chat['timestamp']}", expanded=False):
            st.markdown("**Question:**")
            st.write(chat['question'])
            st.markdown("**Answer:**")
            st.write(chat['answer'])

# Main Content (Column 2)
with col2:
    st.title("Employment Rights and Legal Advice Chatbot")

    # Language selector with translation function
    selected_language = st.selectbox("Select Language", ["English", "Hindi", "Tamil", "Telugu", "Malayalam", "Kannada"])

    # Input type selection
    input_type = st.radio("Choose Input Type", ("Text", "Voice", "Document Image"))

    # If "Text" is selected, show the text input and handle it
    if input_type == "Text":
        # Text-based input
        user_query = st.text_area(
            "Enter your question about employment rights:",
            height=100,
            placeholder="Example: What are my rights regarding overtime pay?"
        )

        if st.button("Get Legal Advice"):
            if user_query:
                with st.spinner("Getting legal advice..."):
                    response = get_legal_response(user_query)
                
                # Add to chat history
                add_to_chat_history(user_query, response)
                
                st.markdown("### Legal Advice")
                st.markdown(response)
                
                with st.spinner("Generating audio..."):
                    audio_file = generate_audio_response(response)
                
                st.audio(audio_file)
                st.download_button('Download response as text', response, 'legal_advice.txt')
            else:
                st.warning("Please enter a question to get legal advice.")

    # If "Voice" is selected, show voice input options
    elif input_type == "Voice":
        st.markdown("### Voice Input")
        duration = st.slider("Recording duration (seconds)", 1, 10, 5)
        
        if st.button("Start Recording"):
            with st.spinner("Recording..."):
                audio_file = record_audio(duration)
                st.success("Recording completed!")
                
            with st.spinner("Transcribing..."):
                transcribed_text = speech_to_text(audio_file)
                st.markdown("### Transcribed Question")
                st.write(transcribed_text)
                
                if transcribed_text and transcribed_text != "Speech could not be understood":
                    with st.spinner("Getting legal advice..."):
                        response = get_legal_response(transcribed_text)
                    
                    # Add to chat history
                    add_to_chat_history(transcribed_text, response)
                    
                    st.markdown("### Legal Advice")
                    st.markdown(response)
                    
                    with st.spinner("Generating audio..."):
                        audio_file = generate_audio_response(response)
                    
                    st.audio(audio_file)
                    st.download_button('Download response as text', response, 'legal_advice.txt')
                else:
                    st.error("Could not understand the speech. Please try again.")

    # If "Document Image" is selected, show the analyze button immediately
    elif input_type == "Document Image":
        st.markdown("### Document Analysis")
        
        # Create a clickable link styled as a button using HTML
        st.markdown("""
            <a href="http://localhost:8502/" target="_blank" 
               style="
                  background-color: #4CAF50;
                  border: none;
                  color: white;
                  padding: 15px 32px;
                  text-align: center;
                  text-decoration: none;
                  display: inline-block;
                  font-size: 16px;
                  margin: 4px 2px;
                  cursor: pointer;
                  border-radius: 4px;">
                Analyze Document
            </a>
        """, unsafe_allow_html=True)

    # Display current conversation
    if st.session_state['messages']:
        st.markdown("### Current Conversation")
        for message in st.session_state['messages']:
            role = "You" if message["role"] == "user" else "Assistant"
            with st.container():
                st.markdown(f"**{role}:** {message['content']}")