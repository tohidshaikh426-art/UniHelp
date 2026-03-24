# Update file_uploads.py with better error logging
new_upload_route = '''@file_uploads.route('/upload_ticket_file', methods=['POST'])
def upload_ticket_file():
    """Handle ticket file upload with validation"""
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
        
        # Ensure upload folder exists
        try:
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            print(f"✅ Upload folder ready: {UPLOAD_FOLDER}")
        except Exception as folder_error:
            print(f"❌ Error creating upload folder: {folder_error}")
            return jsonify({
                'success': False,
                'error': 'Server configuration error'
            }), 500
        
        # Save file
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        print(f"💾 Saving to: {filepath}")
        
        try:
            file.save(filepath)
            print(f"✅ File saved successfully")
        except Exception as save_error:
            print(f"❌ Error saving file: {save_error}")
            print(f"Traceback: {traceback.format_exc()}")
            return jsonify({
                'success': False,
                'error': f'Failed to save file: {str(save_error)}'
            }), 500
        
        # Verify file was saved successfully
        if not os.path.exists(filepath):
            print(f"❌ File doesn't exist after save: {filepath}")
            return jsonify({
                'success': False,
                'error': 'Failed to save uploaded file'
            }), 500
        
        file_size = os.path.getsize(filepath)
        print(f"✅ File uploaded successfully: {filepath} (Size: {file_size} bytes)")
        
        # Return success with file info
        return jsonify({
            'success': True,
            'message': 'File uploaded successfully!',
            'filename': filename,
            'filepath': filepath,
            'url': f'/uploads/{filename}'
        })
    
    except Exception as e:
        print(f"❌ Upload error: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Upload failed: {str(e)}'
        }), 500'''

# Read the file
with open('file_uploads.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the route
old_route_start = "@file_uploads.route('/upload_ticket_file', methods=['POST'])"
old_route_end = "        }), 500\n\n@file_uploads.route('/uploads/<filename>')\n"

start_idx = content.find(old_route_start)
end_idx = content.find("@file_uploads.route('/uploads/<filename>')")

if start_idx != -1 and end_idx != -1:
    # Replace the route
    new_content = content[:start_idx] + new_upload_route + "\n\n" + content[end_idx:]
    
    # Write back
    with open('file_uploads.py', 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print("✅ file_uploads.py updated with detailed error logging!")
else:
    print("❌ Could not find the route to replace")
    print(f"Start found: {start_idx}, End found: {end_idx}")
