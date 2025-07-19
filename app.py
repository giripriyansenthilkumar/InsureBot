from werkzeug.security import generate_password_hash

from flask import Flask, render_template, request, jsonify, session
from pymongo import MongoClient
from werkzeug.security import check_password_hash
# Import RAG model
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from rag_brain import get_response

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # Replace with a secure key

# MongoDB setup
# MongoDB setup
client = MongoClient('mongodb+srv://ml_dept_project:ml_dept_project@ml-project.gkigx.mongodb.net/')  # Update with your MongoDB URI if needed
db = client['InsureBot']
users_collection = db['users']

# Registration API endpoint
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    name = data.get('name')
    password = data.get('password')

    if not email or not name or not password:
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400

    if users_collection.find_one({'email': email}):
        return jsonify({'success': False, 'message': 'Email already registered'}), 409

    hashed_password = generate_password_hash(password)

    # Default settings
    default_settings = {
        "defaultMode": "text",
        "autoSaveHistory": True,
        "autoExport": False,
        "soundNotifications": True,
        "desktopNotifications": False,
        "retentionPeriod": "90",
        "microphoneDevice": "default",
        "recognitionLanguage": "en-US",
        "fontSize": "medium",
        "theme": "dark",
        "colorScheme": "blue"
    }

    user_doc = {
        'email': email,
        'password': hashed_password,
        'name': name,
        'settings': default_settings
    }
    users_collection.insert_one(user_doc)
    return jsonify({'success': True, 'message': 'Registration successful'})

# Home page
@app.route('/')
def index():
    return render_template('index.html')

# Main chat interface
@app.route('/main_chat_interface')
def main_chat_interface():
    user_name = session.get('user_name', 'Guest')
    return render_template('main_chat_interface.html', user_name=user_name)

# Chat history
@app.route('/chat_history')
def chat_history():
    return render_template('chat_history.html')

# User settings
@app.route('/user_settings')
def user_settings():
    return render_template('user_settings.html')

# User registration
@app.route('/user_registration')
def user_registration():
    return render_template('user_registration.html')

# User login
# User login
@app.route('/user_login')
def user_login():
    return render_template('user_login.html')

# Login API endpoint
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = users_collection.find_one({'email': email})
    if user and check_password_hash(user['password'], password):
        session['user_name'] = user.get('name', '')
        session['user_email'] = user.get('email', '')
        return jsonify({'success': True, 'message': 'Login successful'})
    else:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

# About page
@app.route('/about')
def about():
    return render_template('about.html')

# Privacy policy
@app.route('/privacy_policy')
def privacy_policy():
    return render_template('privacy_policy.html')

# Terms of service
@app.route('/terms_of_service')
def terms_of_service():
    return render_template('terms_of_service.html')

# Chatbot query API endpoint
@app.route('/chatbot_query', methods=['POST'])
def chatbot_query():
    data = request.get_json()
    message = data.get('message', '')
    if not message:
        return jsonify({'success': False, 'error': 'No message provided'}), 400
    try:
        response = get_response(message)
        return jsonify({'success': True, 'response': response})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/user_settings', methods=['GET', 'POST'])
def user_settings_api():
    user_email = session.get('user_email')
    if not user_email:
        return jsonify({'success': False, 'error': 'Not logged in'}), 401

    user = users_collection.find_one({'email': user_email})
    if not user:
        return jsonify({'success': False, 'error': 'User not found'}), 404

    if request.method == 'GET':
        settings = user.get('settings', {})
        return jsonify({'success': True, 'settings': settings})

    # POST: update settings
    data = request.get_json()
    new_settings = data or {}
    # Only update allowed fields
    allowed_fields = [
        "defaultMode", "autoSaveHistory", "autoExport", "soundNotifications", "desktopNotifications",
        "retentionPeriod", "microphoneDevice", "recognitionLanguage", "fontSize", "theme", "colorScheme"
    ]
    update_dict = {k: v for k, v in new_settings.items() if k in allowed_fields}
    if not update_dict:
        return jsonify({'success': False, 'error': 'No valid settings provided'}), 400

    users_collection.update_one(
        {'email': user_email},
        {'$set': {f'settings.{k}': v for k, v in update_dict.items()}}
    )
    return jsonify({'success': True, 'message': 'Settings updated'})

if __name__ == '__main__':
    app.run(debug=True)
