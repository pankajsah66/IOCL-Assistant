"""
IOCL ChatGPT-Style Backend API
Flask server with document support, context-based Q&A, and conversation history
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import PyPDF2
import requests
import re
import base64
from werkzeug.utils import secure_filename
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_FILE_EXTENSIONS = {'pdf', 'txt'}
ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
OLLAMA_URL = "https://anjanette-prodistribution-undifferentiably.ngrok-free.dev"
MODEL_NAME = "mistral"

# Context file path
CONTEXT_FILE_PATH = "context.txt"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Storage
content_storage = {}
predefined_context = None
conversation_history = {}  # Store conversation history by conversation_id


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


def build_conversation_context(conversation_id, max_turns=3):
    """Build context from recent conversation history"""
    if conversation_id not in conversation_history or len(conversation_history[conversation_id]) == 0:
        return ""
    
    history = conversation_history[conversation_id][-max_turns:]
    context = "\n\nPrevious conversation:\n"
    
    for item in history:
        context += f"User: {item['question']}\n"
        context += f"Assistant: {item['answer']}\n\n"
    
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
        
        headers = {
            "ngrok-skip-browser-warning": "true"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
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
            "model": "llava",
            "prompt": prompt,
            "images": [image_base64],
            "stream": False
        }
        
        headers = {
            "ngrok-skip-browser-warning": "true"
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=120)
        
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
    """Universal chat endpoint - handles text, images, and files with conversation history"""
    try:
        # Check if request has files
        has_files = 'file' in request.files or 'image' in request.files
        
        if has_files:
            # Handle file/image upload
            if 'image' in request.files:
                image_file = request.files['image']
                conversation_id = request.form.get('conversation_id', 'default')
                
                if image_file and allowed_file(image_file.filename, ALLOWED_IMAGE_EXTENSIONS):
                    filename = secure_filename(image_file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    image_file.save(filepath)
                    
                    image_base64 = encode_image_to_base64(filepath)
                    question = request.form.get('question', 'What is in this image?')
                    
                    # Build conversation context
                    history_context = build_conversation_context(conversation_id)
                    full_prompt = f"{history_context}\n\nCurrent question about image: {question}"
                    
                    answer = analyze_image_with_ollama(image_base64, full_prompt)
                    
                    # Store in conversation history
                    if conversation_id not in conversation_history:
                        conversation_history[conversation_id] = []
                    
                    conversation_history[conversation_id].append({
                        'question': question,
                        'answer': answer,
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    os.remove(filepath)
                    
                    return jsonify({
                        "success": True,
                        "answer": answer,
                        "conversation_id": conversation_id,
                        "type": "image"
                    })
            
            elif 'file' in request.files:
                file = request.files['file']
                conversation_id = request.form.get('conversation_id', 'default')
                
                if file and allowed_file(file.filename, ALLOWED_FILE_EXTENSIONS):
                    filename = secure_filename(file.filename)
                    filepath = os.path.join(UPLOAD_FOLDER, filename)
                    file.save(filepath)
                    
                    file_ext = filename.rsplit('.', 1)[1].lower()
                    if file_ext == 'pdf':
                        extracted_text = extract_text_from_pdf(filepath)
                    else:
                        extracted_text = extract_text_from_txt(filepath)
                    
                    session_id = filename.rsplit('.', 1)[0]
                    content_storage[session_id] = extracted_text
                    
                    question = request.form.get('question', '')
                    
                    if question:
                        context = find_relevant_context(extracted_text, question)
                        history_context = build_conversation_context(conversation_id)
                        
                        prompt = f"""Based on this document content and previous conversation, answer the question:

Document:
{context}
{history_context}

Current question: {question}

Answer:"""
                        answer = ask_ollama(prompt)
                        
                        # Store in conversation history
                        if conversation_id not in conversation_history:
                            conversation_history[conversation_id] = []
                        
                        conversation_history[conversation_id].append({
                            'question': question,
                            'answer': answer,
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        answer = f"File '{filename}' uploaded successfully. You can now ask questions about it."
                    
                    os.remove(filepath)
                    
                    return jsonify({
                        "success": True,
                        "answer": answer,
                        "session_id": session_id,
                        "conversation_id": conversation_id,
                        "type": "document"
                    })
        
        else:
            # Handle text-only question
            data = request.json
            question = data.get('question', '')
            use_context = data.get('use_context', False)
            session_id = data.get('session_id', None)
            conversation_id = data.get('conversation_id', 'default')
            
            if not question:
                return jsonify({"error": "No question provided"}), 400
            
            # Initialize conversation history if needed
            if conversation_id not in conversation_history:
                conversation_history[conversation_id] = []
            
            # Build conversation context
            history_context = build_conversation_context(conversation_id)
            
            # Priority: 1. Session document, 2. Predefined context, 3. General question
            if session_id and session_id in content_storage:
                context = find_relevant_context(content_storage[session_id], question)
                prompt = f"""Based on this document content and previous conversation, answer the question:

Document:
{context}
{history_context}

Current question: {question}

Answer:"""
            elif use_context and predefined_context:
                context = find_relevant_context(predefined_context, question)
                prompt = f"""Based on this context and previous conversation, answer the question:

Context:
{context}
{history_context}

Current question: {question}

Answer:"""
            else:
                if history_context:
                    prompt = f"""{history_context}

Current question: {question}

Answer:"""
                else:
                    prompt = question
            
            answer = ask_ollama(prompt)
            
            # Store in conversation history
            conversation_history[conversation_id].append({
                'question': question,
                'answer': answer,
                'timestamp': datetime.now().isoformat()
            })
            
            # Keep only last 20 exchanges to avoid memory issues
            if len(conversation_history[conversation_id]) > 20:
                conversation_history[conversation_id] = conversation_history[conversation_id][-20:]
            
            return jsonify({
                "success": True,
                "answer": answer,
                "conversation_id": conversation_id,
                "type": "text"
            })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/clear-conversation', methods=['POST'])
def clear_conversation():
    """Clear conversation history for a specific conversation_id"""
    try:
        data = request.json
        conversation_id = data.get('conversation_id', 'default')
        
        if conversation_id in conversation_history:
            del conversation_history[conversation_id]
        
        return jsonify({
            "success": True,
            "message": f"Conversation '{conversation_id}' cleared"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/conversation-history', methods=['GET'])
def get_conversation_history():
    """Get conversation history for a specific conversation_id"""
    try:
        conversation_id = request.args.get('conversation_id', 'default')
        
        history = conversation_history.get(conversation_id, [])
        
        return jsonify({
            "success": True,
            "conversation_id": conversation_id,
            "history": history,
            "count": len(history)
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/api/context-status', methods=['GET'])
def context_status():
    """Check if context file is loaded"""
    return jsonify({
        "loaded": predefined_context is not None,
        "file_path": CONTEXT_FILE_PATH,
        "active_conversations": len(conversation_history),
        "total_messages": sum(len(history) for history in conversation_history.values())
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
    
    load_context_file()
    
    print("-" * 60)
    print("Server starting on http://localhost:5000")
    print("=" * 60)
    
    app.run(debug=True, host='0.0.0.0', port=5000)