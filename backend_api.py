"""
IOCL ChatGPT-Style Backend API
Flask server with document support and context-based Q&A
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import requests
import re
import base64
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_FILE_EXTENSIONS = {'pdf', 'txt'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
OLLAMA_URL = "http://localhost:11434"
MODEL_NAME = "mistral"

# Context file path
CONTEXT_FILE_PATH = "context.txt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Store content in memory
content_storage = {}
predefined_context = None


def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions


def extract_text_from_pdf(pdf_path):
    """Extract text from PDF file"""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF: {e}")
        return None


def extract_text_from_txt(txt_path):
    """Extract text from TXT file"""
    try:
        with open(txt_path, 'r', encoding='utf-8') as file:
            return file.read()
    except Exception as e:
        print(f"Error reading TXT: {e}")
        return None


def encode_image_to_base64(image_path):
    """Encode image to base64"""
    try:
        with open(image_path, 'rb') as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    except Exception as e:
        print(f"Error encoding image: {e}")
        return None


def find_relevant_context(content, question, max_length=3000):
    """Find relevant sections of content"""
    question_lower = question.lower()
    keywords = re.findall(r'\b\w{4,}\b', question_lower)
    paragraphs = content.split('\n\n')
    
    scored_paragraphs = []
    for para in paragraphs:
        if len(para.strip()) < 20:
            continue
        
        score = 0
        para_lower = para.lower()
        for keyword in keywords:
            if keyword in para_lower:
                score += para_lower.count(keyword)
        
        if score > 0:
            scored_paragraphs.append((score, para))
    
    scored_paragraphs.sort(reverse=True, key=lambda x: x[0])
    
    context = ""
    for score, para in scored_paragraphs[:10]:
        if len(context) + len(para) < max_length:
            context += para + "\n\n"
        else:
            break
    
    if not context:
        context = content[:max_length]
    
    return context


def ask_ollama(prompt, model=MODEL_NAME):
    """Send prompt to Ollama"""
    try:
        url = f"{OLLAMA_URL}/api/generate"
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response from model')
        else:
            return f"Error: Ollama returned status code {response.status_code}"
    
    except Exception as e:
        return f"Error: {str(e)}"


def analyze_image_with_ollama(image_base64, prompt):
    """Analyze image using Ollama vision model (llava)"""
    try:
        url = f"{OLLAMA_URL}/api/generate"
        payload = {
            "model": "llava",  # Vision model
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }
        
        response = requests.post(url, json=payload, timeout=120)
        
        if response.status_code == 200:
            result = response.json()
            return result.get('response', 'No response from model')
        else:
            return f"Error: Ollama returned status code {response.status_code}"
    
    except Exception as e:
        return f"Error: {str(e)}"


def load_context_file():
    """Load predefined context from file"""
    global predefined_context
    try:
        if os.path.exists(CONTEXT_FILE_PATH):
            with open(CONTEXT_FILE_PATH, 'r', encoding='utf-8') as f:
                predefined_context = f.read()
            print(f"✓ Loaded context from: {CONTEXT_FILE_PATH}")
            return True
        else:
            print(f"⚠ Context file not found: {CONTEXT_FILE_PATH}")
            return False
    except Exception as e:
        print(f"Error loading context file: {e}")
        return False


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "ok", "message": "Backend is running"})


@app.route('/api/chat', methods=['POST'])
def chat():
    """Universal chat endpoint - handles text, images, and files"""
    try:
        # Check if request has files
        has_files = 'file' in request.files or 'image' in request.files
        
        if has_files:
            # Handle file/image upload
            if 'image' in request.files:
                image_file = request.files['image']
                if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    # Save image temporarily
                    filename = secure_filename(image_file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    image_file.save(filepath)
                    
                    # Encode to base64
                    image_base64 = encode_image_to_base64(filepath)
                    
                    # Get user question
                    question = request.form.get('question', 'What is in this image?')
                    
                    # Analyze image
                    answer = analyze_image_with_ollama(image_base64, question)
                    
                    # Clean up
                    os.remove(filepath)
                    
                    return jsonify({
                        "success": True,
                        "answer": answer,
                        "type": "image"
                    })
            
            elif 'file' in request.files:
                file = request.files['file']
                if file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    
                    # Extract text
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    if file_ext == 'pdf':
                        extracted_text = extract_text_from_pdf(filepath)
                    else:
                        extracted_text = extract_text_from_txt(filepath)
                    
                    # Store in memory with session ID
                    session_id = filename.rsplit('.', 1)[0]
                    content_storage[session_id] = extracted_text
                    
                    # Get question
                    question = request.form.get('question', '')
                    
                    if question:
                        # Answer question about the file
                        context = find_relevant_context(extracted_text, question)
                        prompt = f"""Based on this document content, answer the question:

Document:
{context}

Question: {question}

Answer:"""
                        answer = ask_ollama(prompt)
                    else:
                        answer = f"File '{filename}' uploaded successfully. You can now ask questions about it."
                    
                    # Clean up file but keep content in memory
                    os.remove(filepath)
                    
                    return jsonify({
                        "success": True,
                        "answer": answer,
                        "session_id": session_id,
                        "type": "document"
                    })
        
        else:
            # Handle text-only question
            data = request.json
            question = data.get('question', '')
            use_context = data.get('use_context', False)
            session_id = data.get('session_id', None)  # Check if there's an active session
            
            if not question:
                return jsonify({"error": "No question provided"}), 400
            
            # Priority: 1. Session document, 2. Predefined context, 3. General question
            if session_id and session_id in content_storage:
                # Use the uploaded document from session
                context = find_relevant_context(content_storage[session_id], question)
                prompt = f"""Based on this document content, answer the question:

Document:
{context}

Question: {question}

Answer:"""
            elif use_context and predefined_context:
                # Use predefined context
                context = find_relevant_context(predefined_context, question)
                prompt = f"""Based on this context, answer the question:

Context:
{context}

Question: {question}

Answer:"""
            else:
                # Direct question without context
                prompt = question
            
            answer = ask_ollama(prompt)
            
            return jsonify({
                "success": True,
                "answer": answer,
                "type": "text"
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/context-status', methods=['GET'])
def context_status():
    """Check if context file is loaded"""
    return jsonify({
        "loaded": predefined_context is not None,
        "file_path": CONTEXT_FILE_PATH
    })


if __name__ == '__main__':
    print("=" * 60)
    print("IOCL ChatGPT-Style Backend API")
    print("=" * 60)
    print(f"Text Model: {MODEL_NAME}")
    print(f"Ollama URL: {OLLAMA_URL}")
    print(f"Context file: {CONTEXT_FILE_PATH}")
    print(f"Image support: Install 'ollama pull llava' for images")
    print("-" * 60)
    
    # Load predefined context
    load_context_file()
    
    print("-" * 60)
    print("Server starting on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)