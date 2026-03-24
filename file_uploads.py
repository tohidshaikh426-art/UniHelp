# file_uploads.py
# File upload management for UniHelp tickets

from flask import Blueprint, jsonify, request, send_from_directory, flash, redirect, url_for
from werkzeug.utils import secure_filename
import os
from datetime import datetime

file_uploads = Blueprint('file_uploads', __name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    """Check if file extension is allowed (images only)"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def check_file_size(file):
    """Check if file size is within limit (5MB)"""
    file.seek(0, 2)  # Seek to end
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    return file_size <= MAX_FILE_SIZE

@file_uploads.route('/upload_ticket_file', methods=['POST'])
def upload_ticket_file():
    """Handle ticket file upload with validation"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                'success': False, 
                'error': 'Invalid file type. Only images (PNG, JPG, JPEG, GIF, WEBP) are allowed.'
            }), 400
        
        if not check_file_size(file):
            return jsonify({
                'success': False, 
                'error': 'File too large. Maximum size is 5MB.'
            }), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"{timestamp}_{original_filename}"
        
        # Ensure upload folder exists
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Return success with file info
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully!',
            'filename': filename,
            'filepath': filepath,
            'url': f'/uploads/{filename}'
        })
    
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@file_uploads.route('/uploads/<filename>')
def serve_uploaded_file(filename):
    """Serve uploaded files"""
    return send_from_directory(UPLOAD_FOLDER, filename)
