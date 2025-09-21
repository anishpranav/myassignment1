#!/usr/bin/env python3
"""
Flask Web Interface for Python Terminal - Vercel Deployment
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import os
import sys
import uuid
import json
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(__file__))

# Import your terminal components
from terminal_core import Terminal
from utils.colors import Colors

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-in-production')
CORS(app)

# Store terminal sessions (in production, use Redis or database)
terminal_sessions = {}

def get_terminal_session(session_id):
    """Get or create a terminal session"""
    if session_id not in terminal_sessions:
        # Create new terminal with virtual filesystem for web safety
        terminal_sessions[session_id] = Terminal(use_virtual=True)
    return terminal_sessions[session_id]

def strip_ansi_codes(text):
    """Remove ANSI color codes from text for web display"""
    import re
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    return ansi_escape.sub('', text)

def format_for_web(text):
    """Format terminal output for web display"""
    if not text:
        return ""
    
    # Strip ANSI codes and convert to HTML
    clean_text = strip_ansi_codes(text)
    
    # Convert newlines to HTML breaks
    html_text = clean_text.replace('\n', '<br>')
    
    # Add basic styling classes (you can enhance this)
    html_text = html_text.replace('Error:', '<span class="error">Error:</span>')
    html_text = html_text.replace('✅', '<span class="success">✅</span>')
    html_text = html_text.replace('❌', '<span class="error">❌</span>')
    html_text = html_text.replace('⚠️', '<span class="warning">⚠️</span>')
    
    return html_text

@app.route('/')
def index():
    """Main terminal interface"""
    return render_template('terminal.html')

@app.route('/api/execute', methods=['POST'])
def execute_command():
    """Execute a command and return result"""
    try:
        data = request.get_json()
        command = data.get('command', '').strip()
        
        if not command:
            return jsonify({'error': 'No command provided'})
        
        # Get or create session
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        terminal = get_terminal_session(session['session_id'])
        
        # Execute command
        output = terminal.execute(command)
        
        # Format output for web
        formatted_output = format_for_web(output)
        
        # Get current directory
        current_dir = terminal.get_current_directory()
        
        return jsonify({
            'output': formatted_output,
            'current_dir': current_dir,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'})

@app.route('/api/ai', methods=['POST'])
def ai_command():
    """Execute AI natural language command"""
    try:
        data = request.get_json()
        query = data.get('query', '').strip()
        
        if not query:
            return jsonify({'error': 'No query provided'})
        
        # Get or create session
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        terminal = get_terminal_session(session['session_id'])
        
        # Execute AI command
        output = terminal.execute(f"ai {query}")
        
        # Format output for web
        formatted_output = format_for_web(output)
        
        # Get current directory
        current_dir = terminal.get_current_directory()
        
        return jsonify({
            'output': formatted_output,
            'current_dir': current_dir,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'})

@app.route('/api/status')
def status():
    """Get terminal status"""
    try:
        if 'session_id' not in session:
            session['session_id'] = str(uuid.uuid4())
        
        terminal = get_terminal_session(session['session_id'])
        current_dir = terminal.get_current_directory()
        
        return jsonify({
            'current_dir': current_dir,
            'session_id': session['session_id'],
            'status': 'ready'
        })
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'})

@app.route('/api/clear')
def clear_session():
    """Clear terminal session"""
    try:
        if 'session_id' in session:
            session_id = session['session_id']
            if session_id in terminal_sessions:
                del terminal_sessions[session_id]
            session['session_id'] = str(uuid.uuid4())
        
        return jsonify({'message': 'Session cleared'})
        
    except Exception as e:
        return jsonify({'error': f'Server error: {str(e)}'})

@app.template_filter('datetime')
def datetime_filter(timestamp):
    """Format datetime for display"""
    if isinstance(timestamp, str):
        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
    else:
        dt = timestamp
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # For local development
    app.run(debug=True, host='0.0.0.0', port=int(os.environ.get('PORT', 8000)))