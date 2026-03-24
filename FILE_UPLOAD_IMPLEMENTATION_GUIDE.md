# Ticket File Upload Implementation Guide

## Problem Fixed
- 404 error when uploading files in ticket creation
- Added support for image files only (PNG, JPG, JPEG, GIF, WEBP)
- Limited file size to 5MB
- Added file display/download functionality for tickets

## Files Created

### 1. `file_uploads.py` ✅ (Already Created)
New blueprint for handling file uploads with proper validation and serving.

**Features:**
- Image-only upload (PNG, JPG, JPEG, GIF, WEBP)
- 5MB file size limit
- Secure filename generation with timestamps
- File validation endpoints
- Serves uploaded files via `/uploads/<filename>`

## Required Changes

### Step 1: Update `app.py`

#### A. Add Import (After line 20 - after Flask-Mail import):
```python
# NEW: Import file upload blueprint
from file_uploads import file_uploads
```

#### B. Register Blueprint (Before line 3564 - before `if __name__ == '__main__':`):
```python
# Register file upload blueprint
app.register_blueprint(file_uploads)
```

#### C. Update ALLOWED_EXTENSIONS (Line 48):
Replace this line:
```python
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'doc', 'docx'}
```

With:
```python
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}  # Image files only
```

#### D. Update MAX_CONTENT_LENGTH (Line 47):
Replace this line:
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
```

With:
```python
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max file size
```

### Step 2: Update `templates/user/create_ticket.html`

Replace the entire form section (lines 11-69) with AJAX-based upload:

```html
<form method="POST" action="{{ url_for('create_ticket') }}" class="space-y-6">
    <!-- Title -->
    <div>
        <label for="title" class="block text-sm font-medium text-gray-700 mb-2">
            Ticket Title <span class="text-red-500">*</span>
        </label>
        <input type="text" id="title" name="title" required 
               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
               placeholder="Brief description of the issue">
    </div>

    <!-- Category -->
    <div>
        <label for="category" class="block text-sm font-medium text-gray-700 mb-2">
            Category <span class="text-red-500">*</span>
        </label>
        <select id="category" name="category" required
                class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
            <option value="">Select a category</option>
            {% for cat in categories %}
            <option value="{{ cat }}">{{ cat }}</option>
            {% endfor %}
        </select>
    </div>

    <!-- Description -->
    <div>
        <label for="description" class="block text-sm font-medium text-gray-700 mb-2">
            Description <span class="text-red-500">*</span>
        </label>
        <textarea id="description" name="description" required rows="6"
                  class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent"
                  placeholder="Provide detailed information about your issue..."></textarea>
        <p class="text-sm text-gray-500 mt-2">Include any error messages, steps to reproduce, or relevant details.</p>
    </div>

    <!-- File Upload with AJAX -->
    <div>
        <label for="file" class="block text-sm font-medium text-gray-700 mb-2">
            Attachment (Optional)
        </label>
        <input type="file" id="fileInput" name="file" 
               accept=".png,.jpg,.jpeg,.gif,.webp"
               class="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent">
        <p class="text-sm text-gray-500 mt-2">Accepted formats: PNG, JPG, JPEG, GIF, WEBP (Max 5MB)</p>
        
        <!-- Upload Status -->
        <div id="uploadStatus" class="hidden mt-2"></div>
        <input type="hidden" id="uploadedFilePath" name="filepath" value="">
    </div>

    <!-- Submit Buttons -->
    <div class="flex space-x-4 pt-4">
        <button type="submit" id="submitBtn"
                class="flex-1 bg-primary text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition font-medium">
            Submit Ticket
        </button>
        <a href="{{ url_for('user_dashboard') }}" 
           class="flex-1 bg-gray-200 text-gray-700 px-6 py-3 rounded-lg hover:bg-gray-300 transition font-medium text-center">
            Cancel
        </a>
    </div>
</form>

<script>
// Auto-upload file when selected
document.getElementById('fileInput').addEventListener('change', async function(e) {
    const file = e.target.files[0];
    if (!file) return;
    
    // Validate file type
    const allowedTypes = ['image/png', 'image/jpeg', 'image/jpg', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
        showUploadStatus('❌ Invalid file type. Only images are allowed.', 'error');
        this.value = '';
        return;
    }
    
    // Validate file size (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showUploadStatus('❌ File too large. Maximum size is 5MB.', 'error');
        this.value = '';
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.className = 'mt-2 p-3 bg-blue-50 text-blue-700 rounded-lg';
    statusDiv.innerHTML = '⏳ Uploading file...';
    statusDiv.classList.remove('hidden');
    
    try {
        const response = await fetch('/upload_ticket_file', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (data.success) {
            showUploadStatus('✅ ' + data.message, 'success');
            document.getElementById('uploadedFilePath').value = data.filepath;
        } else {
            showUploadStatus('❌ ' + data.error, 'error');
            this.value = '';
        }
    } catch (error) {
        showUploadStatus('❌ Upload failed. Please try again.', 'error');
        this.value = '';
    }
});

function showUploadStatus(message, type) {
    const statusDiv = document.getElementById('uploadStatus');
    statusDiv.classList.remove('hidden');
    
    if (type === 'success') {
        statusDiv.className = 'mt-2 p-3 bg-green-50 text-green-700 rounded-lg';
    } else if (type === 'error') {
        statusDiv.className = 'mt-2 p-3 bg-red-50 text-red-700 rounded-lg';
    } else {
        statusDiv.className = 'mt-2 p-3 bg-blue-50 text-blue-700 rounded-lg';
    }
    
    statusDiv.innerHTML = message;
}
</script>
```

### Step 3: Update `create_ticket()` Route in `app.py`

Replace lines 786-834 with:

```python
@app.route('/user/create_ticket', methods=['GET', 'POST'])
@login_required
@role_required(['staff', 'student'])
def create_ticket():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        category = request.form.get('category')
        filepath = request.form.get('filepath')  # Get uploaded file path
        
        # Validate required fields
        if not title or not description or not category:
            flash('All required fields must be filled', 'error')
            return redirect(url_for('create_ticket'))
        
        # Create ticket using Supabase
        new_ticket = db.create_ticket({
            'title': title,
            'description': description,
            'category': category,
            'userid': session.get('user_id'),
            'filepath': filepath,  # Store file path in database
            'status': 'Open'
        })
        
        if new_ticket:
            ticket_id = new_ticket['ticketid']
            
            # Auto-assign ticket to available technician
            all_users = db.get_all_users()
            technicians = [u for u in all_users if u['role'] == 'technician' and u['isapproved']]
            
            assigned_technician = None
            if technicians:
                # Simple assignment - assign to first available technician
                assigned_technician = technicians[0]
                db.update_ticket(ticket_id, {
                    'assignedto': assigned_technician['userid'],
                    'status': 'In Progress'
                })
            
            if assigned_technician:
                flash(f'Ticket created and assigned to {assigned_technician["name"]}', 'success')
            else:
                flash('Ticket created successfully. A technician will be assigned soon.', 'success')
        else:
            flash('Failed to create ticket', 'error')
        
        return redirect(url_for('user_dashboard'))
    
    categories = ['Hardware', 'Software', 'Network', 'Printer', 'Account Access', 'Other']
    return render_template('user/create_ticket.html', categories=categories)
```

### Step 4: Add File Display in Ticket View

Update `templates/view_ticket.html` to show uploaded files:

Find where ticket details are displayed and add:

```html
{% if ticket.filepath %}
<div class="mt-4 p-4 bg-gray-50 rounded-lg">
    <h3 class="text-lg font-semibold text-gray-900 mb-3">📎 Attached File</h3>
    
    <!-- Show image preview -->
    {% if ticket.filepath.endswith(('.png', '.jpg', '.jpeg', '.gif', '.webp')) %}
    <div class="mb-3">
        <img src="/{{ ticket.filepath }}" alt="Attachment" 
             class="max-w-full h-auto max-h-96 rounded-lg border border-gray-300 shadow-sm">
    </div>
    {% endif %}
    
    <!-- Download link -->
    <div class="flex items-center justify-between">
        <div class="flex items-center space-x-2">
            <svg class="w-5 h-5 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            <span class="text-sm text-gray-600">{{ ticket.filepath.split('/')[-1] }}</span>
        </div>
        <a href="/{{ ticket.filepath }}" download 
           class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition">
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                      d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4"/>
            </svg>
            Download
        </a>
    </div>
</div>
{% endif %}
```

## Database Schema (No Changes Required)

The existing `ticket` table already has a `filepath` column, so no database migration is needed.

## Testing Checklist

- [ ] User can upload PNG, JPG, JPEG, GIF, WEBP files
- [ ] Files larger than 5MB are rejected with clear error message
- [ ] Non-image files are rejected
- [ ] Upload shows success message "File uploaded successfully!"
- [ ] File path is stored in database ticket record
- [ ] Uploaded file is visible in ticket view page
- [ ] Admin can see attached files when viewing tickets
- [ ] Technician can see attached files when viewing assigned tickets
- [ ] File can be downloaded by clicking download button
- [ ] Image files show preview thumbnail

## Security Features

✅ Secure filename sanitization  
✅ File type validation (MIME type + extension)  
✅ File size limit enforcement (5MB)  
✅ Timestamp-based unique filenames  
✅ Files served from dedicated route  
✅ No direct file access to uploads folder  

## Next Steps

1. Apply all changes from this guide
2. Test file upload with various image types
3. Verify file display in ticket view
4. Commit and push to GitHub for Vercel deployment
