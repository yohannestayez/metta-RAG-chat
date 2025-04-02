# app.py
from sys import path
path.append('src')
from flask import Flask, request, jsonify, render_template
import os
from werkzeug.utils import secure_filename
from KG_add import update_knowledge_base
from chatbot import _generate_response
from gemini import GeminiModel

llm=GeminiModel()

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def handle_request():
    # Handle PDF upload
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(file_path)
            try:
                update_knowledge_base(file_path)
                os.remove(file_path)
                return jsonify({'status': 'success', 'message': 'Knowledge base updated successfully'})
            except Exception as e:
                return jsonify({'status': 'error', 'message': str(e)}), 500

    # Handle text query
    elif request.json and 'text' in request.json:
        try:
            user_query = request.json['text']
            response_type = llm.generate(f"""
                If the query is a simple greeting like 'hi', 'hello', 'hey', or similar, respond with a friendly greeting (e.g., 'Hello there!'). 
                If it’s not a simple greeting, return an empty string (''). 
                The query: {user_query}
            """)
            if response_type.strip():  # Check if LLM returned a non-empty response
                return jsonify({'response': response_type})
            else:
                response = 'hi'  # Non-greeting case
                response = _generate_response(user_query)  # Proceed to further processing
                return jsonify({'response': response})
            
        except Exception as e:
            return jsonify({'status': 'error', 'message': str(e)}), 500

    return jsonify({'status': 'error', 'message': 'Invalid request format'}), 400

if __name__ == '__main__':
    app.run(debug=True)