# Update view_ticket.html with improved attachment display
with open('templates/view_ticket.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the attachment section
old_attachment = '''            <!-- Attachment -->
            {% if ticket.filepath %}
            <div class="pt-6 border-t border-gray-200">
                <p class="text-sm font-medium text-gray-600 mb-2">Attachment</p>
                <a href="/{{ ticket.filepath }}" target="_blank" 
                   class="inline-flex items-center text-primary hover:text-blue-700">
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                    </svg>
                    View Attachment
                </a>
            </div>
            {% endif %}'''

new_attachment = '''            <!-- Attachment -->
            {% if ticket.filepath %}
            <div class="pt-6 border-t border-gray-200">
                <p class="text-sm font-medium text-gray-600 mb-3">📎 Attached File</p>
                
                <!-- Image Preview for image files -->
                {% if '.png' in ticket.filepath or '.jpg' in ticket.filepath or '.jpeg' in ticket.filepath or '.gif' in ticket.filepath or '.webp' in ticket.filepath %}
                <div class="mb-4">
                    <img src="{{ ticket.public_url or '/uploads/' + ticket.filepath.split('/')[-1] }}" 
                         alt="Attachment" 
                         class="max-w-full h-auto max-h-96 rounded-lg border border-gray-300 shadow-sm hover:shadow-md transition">
                </div>
                {% endif %}
                
                <!-- File Info and Action Buttons -->
                <div class="bg-gray-50 rounded-lg p-4">
                    <div class="flex items-center justify-between flex-wrap gap-3">
                        <div class="flex items-center space-x-3">
                            <!-- File Icon -->
                            {% if '.png' in ticket.filepath or '.jpg' in ticket.filepath or '.jpeg' in ticket.filepath or '.gif' in ticket.filepath or '.webp' in ticket.filepath %}
                            <svg class="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                            {% else %}
                            <svg class="w-8 h-8 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                            </svg>
                            {% endif %}
                            
                            <div>
                                <p class="text-sm font-medium text-gray-900">{{ ticket.filepath.split('/')[-1] }}</p>
                                <p class="text-xs text-gray-500">Click download to view or save file</p>
                            </div>
                        </div>
                        
                        <div class="flex space-x-2">
                            <!-- View/Open Button -->
                            <a href="{{ ticket.public_url or '/uploads/' + ticket.filepath.split('/')[-1] }}" 
                               target="_blank"
                               class="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition font-medium">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                                </svg>
                                View
                            </a>
                            
                            <!-- Download Button -->
                            <a href="{{ ticket.public_url or '/uploads/' + ticket.filepath.split('/')[-1] }}" 
                               download
                               class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Download
                            </a>
                        </div>
                    </div>
                </div>
            </div>
            {% endif %}'''

if old_attachment in content:
    content = content.replace(old_attachment, new_attachment)
    
    # Write back
    with open('templates/view_ticket.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ view_ticket.html updated with image preview and download buttons!")
else:
    print("❌ Could not find attachment section to replace")
    print("Searching for partial match...")
    if '{% if ticket.filepath %}' in content:
        print("Found filepath check - attachment section exists but format differs")
