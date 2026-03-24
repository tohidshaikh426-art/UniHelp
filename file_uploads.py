# file_uploads.py
# File upload management for UniHelp tickets using Supabase Storage

from flask import Blueprint, jsonify, request
from werkzeug.utils import secure_filename
from supabase_client import db
import os
from datetime import datetime

file_uploads = Blueprint('file_uploads', __name__)

# Configuration - No longer needed with Supabase Storage
# UPLOAD_FOLDER = 'uploads'  # Removed - using Supabase Storage instead
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
    """Handle ticket file upload with validation using Supabase Storage"""
    import traceback
    
    try:
        print("📥 Starting file upload process...")
        
        if 'file' not in request.files:
            print("❌ No file in request")
            return jsonify({'success': False, 'error': 'No file provided'}), 400
        
        file = request.files['file']
        print(f"📄 File received: {file.filename}, Type: {file.content_type}")
        
        if file.filename == '':
            print("❌ Empty filename")
            return jsonify({'success': False, 'error': 'No file selected'}), 400
        
        if not allowed_file(file.filename):
            print(f"❌ Invalid file type: {file.filename}")
            return jsonify({
                'success': False, 
                'error': 'Invalid file type. Only images (PNG, JPG, JPEG, GIF, WEBP) are allowed.'
            }), 400
        
        if not check_file_size(file):
            print(f"❌ File too large: {file.filename}")
            return jsonify({
                'success': False, 
                'error': 'File too large. Maximum size is 5MB.'
            }), 400
        
        # Generate unique filename
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        original_filename = secure_filename(file.filename)
        filename = f"{timestamp}_{original_filename}"
        print(f"📝 Generated filename: {filename}")
        
        # Read file data
        file_data = file.read()
        file_size = len(file_data)
        print(f"📊 File size: {file_size} bytes")
        
        # Upload to Supabase Storage
        try:
            # Create bucket name
            bucket_name = 'ticket-attachments'
            
            # Create path in storage (organize by date)
            file_path = f"tickets/{datetime.now().strftime('%Y/%m/%d')}/{filename}"
            
            print(f"🗄️ Uploading to Supabase Storage: {bucket_name}/{file_path}")
            
            # Upload file to Supabase Storage
            response = db.client.storage.from_(bucket_name).upload(
                file_path,
                file_data,
                {'content-type': file.content_type}
            )
            
            print(f"✅ Upload successful: {response}")
            
            # Get public URL
            public_url_response = db.client.storage.from_(bucket_name).get_public_url(file_path)
            public_url = public_url_response
            
            print(f"🔗 Public URL: {public_url}")
            
            # Return success with file info
            # Store the file_path (not full URL) in database for reference
            return jsonify({
                'success': True,
                'message': 'File uploaded successfully!',
                'filename': filename,
                'filepath': f'supabase://{bucket_name}/{file_path}',  # Custom protocol for Supabase Storage
                'public_url': public_url,
                'file_size': file_size,
                'content_type': file.content_type
            })
            
        except Exception as storage_error:
            print(f"❌ Supabase Storage error: {storage_error}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': f'Storage upload failed: {str(storage_error)}'
            }), 500
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500

@file_uploads.route('/uploads/<path:file_path>')
def serve_uploaded_file(file_path):
    """Redirect to Supabase Storage public URL"""
    try:
        # Extract bucket and path from stored filepath
        # Format: supabase://bucket_name/path/to/file
        if file_path.startswith('supabase://'):
            parts = file_path.replace('supabase://', '').split('/', 1)
            bucket_name = parts[0]
            file_path_in_bucket = parts[1]
            
            # Get public URL
            public_url = db.client.storage.from_(bucket_name).get_public_url(file_path_in_bucket)
            
            # Redirect to public URL
            from flask import redirect
            return redirect(public_url)
        else:
            return jsonify({'error': 'Invalid file path format'}), 400
    except Exception as e:
        print(f"❌ Error serving file: {e}")
        return jsonify({'error': str(e)}), 500
