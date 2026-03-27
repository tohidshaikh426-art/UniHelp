from flask import Flask, render_template, request, jsonify, session
import google.generativeai as genai
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()
app = Flask(__name__)
app.secret_key = 'ai-bot-secret-key-2026'

# Configure Gemini
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
model = genai.GenerativeModel('gemini-1.5-flash')

# System prompt for UniHelp AI Assistant
SYSTEM_PROMPT = """
You are UniHelp AI Assistant, an intelligent IT helpdesk bot for university students and staff.
Your role: Provide quick IT support, troubleshoot common issues, and escalate complex problems.

Capabilities:
1. Hardware: Laptops, printers, monitors
2. Software: Office apps, browsers, OS issues  
3. Network: WiFi, VPN, internet
4. Accounts: Passwords, login, permissions
5. Email: Outlook, Gmail, university mail

Response style:
- Friendly and empathetic
- Step-by-step troubleshooting
- Ask clarifying questions
- Offer escalation after 3-4 exchanges
- Use simple language

When to escalate:
- Hardware failure
- Account lockout
- Network outages
- After 4 unanswered troubleshooting steps

Always end with: "Need human help? Click 'Connect Technician'"
"""

chat_sessions = {}

@app.route('/')
def home():
    return render_template('ai-bot.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    user_msg = request.json['message']
    session_id = session.get('session_id', str(datetime.now().timestamp()))
    session['session_id'] = session_id
    
    if session_id not in chat_sessions:
        chat_sessions[session_id] = []
    
    # Add user message
    chat_sessions[session_id].append({'role': 'user', 'content': user_msg})
    
    # Limit context to last 8 messages
    context = chat_sessions[session_id][-8:]
    
    try:
        # Generate response with system prompt + context
        response = model.generate_content([
            SYSTEM_PROMPT,
            *context
        ])
        
        bot_reply = response.text
        
        # Add bot response to history
        chat_sessions[session_id].append({'role': 'assistant', 'content': bot_reply})
        
        return jsonify({'reply': bot_reply, 'session_id': session_id})
        
    except Exception as e:
        return jsonify({'reply': f"Sorry, I'm having trouble. Try: 'my wifi isn't working' or 'can't print'"})

if __name__ == '__main__':
    app.run(debug=True, port=5001)
