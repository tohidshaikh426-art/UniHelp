# Fix view_ticket.html - Remove inline image preview, keep only buttons
with open('templates/view_ticket.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the inline image preview section (keep only file info and buttons)
old_preview_section = '''                <!-- Image Preview for image files -->
                {% if '.png' in ticket.filepath or '.jpg' in ticket.filepath or '.jpeg' in ticket.filepath or '.gif' in ticket.filepath or '.webp' in ticket.filepath %}
                <div class="mb-4">
                    <img src="{{ public_url or '/uploads/' + ticket.filepath.split('/')[-1] }}" 
                         alt="Attachment" 
                         class="max-w-full h-auto max-h-96 rounded-lg border border-gray-300 shadow-sm hover:shadow-md transition">
                </div>
                {% endif %}
                
                <!-- File Info and Action Buttons -->'''

new_preview_section = '''                <!-- File Info and Action Buttons -->'''

if old_preview_section in content:
    content = content.replace(old_preview_section, new_preview_section)
    
    # Write back
    with open('templates/view_ticket.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Removed inline image preview from ticket view!")
else:
    print("❌ Could not find image preview section to remove")
