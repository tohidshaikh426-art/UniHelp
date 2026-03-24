# Fix create_ticket to use AJAX uploaded filepath
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the create_ticket POST handling
old_code = '''def create_ticket():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        
        filepath = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
        
        # Create ticket using Supabase
        new_ticket = db.create_ticket({
            'title': title,
            'description': description,
            'category': category,
            'userid': session.get('user_id'),
            'filepath': filepath,
            'status': 'Open'
        })'''

new_code = '''def create_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        
        # Get filepath from AJAX upload (stored in hidden field)
        filepath = request.form.get('filepath')  # This will be supabase://... format
        
        print(f"📝 Creating ticket with filepath: {filepath}")
        
        # Create ticket using Supabase
        new_ticket = db.create_ticket({
            'title': title,
            'description': description,
            'category': category,
            'userid': session.get('user_id'),
            'filepath': filepath,  # Store supabase:// path
            'status': 'Open'
        })'''

if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py updated - create_ticket now uses AJAX uploaded filepath!")
else:
    print("❌ Could not find create_ticket code to replace")
