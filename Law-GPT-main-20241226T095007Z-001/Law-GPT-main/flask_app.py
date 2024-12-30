# app.py
from flask import Flask, render_template, request, jsonify, send_file
import os
import time
from werkzeug.utils import secure_filename
import base64
from io import BytesIO
from gtts import gTTS
import uuid

app = Flask(_name_)
app.config['SECRET_KEY'] = 'your-secret-key-here'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['AUDIO_FOLDER'] = 'audio'

# Ensure required folders exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['AUDIO_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)


def generate_story_from_text(prompt):
    """Generate story based on text input"""
    # Simulate story generation with different themes
    theme = "default"
    for theme_key in theme_prompts:
        if theme_key.lower() in prompt.lower():
            theme = theme_key.lower()
            break
            
    time.sleep(2)  # Simulate API delay
    
    
    
    return stories.get(theme, stories["default"]) + "\n\nBased on prompt: " + prompt

def generate_image_caption(image_file):
    """Generate caption for uploaded image"""
    

    import random
    time.sleep(2)  # Simulate API delay
    return random.choice(captions)

def generate_audio_from_story(text):
    """Generate audio file from story text"""
    try:
        # Generate a unique filename for each audio
        filename = f"story_{uuid.uuid4().hex[:8]}.mp3"
        filepath = os.path.join(app.config['AUDIO_FOLDER'], filename)
        
        # Generate audio using gTTS
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(filepath)
        
        return filename
    except Exception as e:
        print(f"Error generating audio: {str(e)}")
        return None

@app.route('/')
def index():
    return render_template('home.html', 
                         categories=categories,
                         theme_prompts=theme_prompts)

@app.route('/generate-story', methods=['POST'])
def generate_story():
    try:
        data = request.json
        input_type = data.get('inputType')
        selected_theme = data.get('selectedTheme')
        
        if input_type == 'text':
            input_text = data.get('inputText')
            prompt = f"{theme_prompts[selected_theme]} {input_text}"
            story = generate_story_from_text(prompt)
        else:
            image_data = data.get('uploadedImage')
            if not image_data:
                return jsonify({'error': 'Please upload an image first'}), 400
                
            # Process base64 image
            image_data = image_data.split(',')[1]
            image_binary = base64.b64decode(image_data)
            
            # Save temporary file
            temp_path = os.path.join(app.config['UPLOAD_FOLDER'], 'temp_image.jpg')
            with open(temp_path, 'wb') as f:
                f.write(image_binary)
            
            caption = generate_image_caption(temp_path)
            prompt = f"{theme_prompts[selected_theme]} {caption}"
            story = generate_story_from_text(prompt)
            
            # Clean up
            os.remove(temp_path)
        
        # Generate audio
        audio_filename = generate_audio_from_story(story)
        
        if audio_filename:
            audio_url = f"/audio/{audio_filename}"
        else:
            audio_url = None
        
        return jsonify({
            'story': story,
            'audioUrl': audio_url
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/audio/<filename>')
def serve_audio(filename):
    return send_file(
        os.path.join(app.config['AUDIO_FOLDER'], filename),
        mimetype='audio/mpeg'
    )

@app.route('/download-story', methods=['POST'])
def download_story():
    try:
        story = request.json.get('story')
        if not story:
            return jsonify({'error': 'No story provided'}), 400
            
        # Create temporary file
        temp_file = BytesIO()
        temp_file.write(story.encode())
        temp_file.seek(0)
        
        return send_file(
            temp_file,
            as_attachment=True,
            download_name='second.html',
            mimetype='text/plain'
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if _name_ == '_main_':
    app.run(debug=True)