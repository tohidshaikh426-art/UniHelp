# Fix download button to work with cross-origin Supabase URLs
with open('templates/view_ticket.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and replace the download button with JavaScript-powered download
old_download_button = '''                            <!-- Download Button -->
                            <a href="{{ public_url or '/uploads/' + ticket.filepath.split('/')[-1] }}" 
                               download
                               class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Download
                            </a>'''

new_download_button = '''                            <!-- Download Button -->
                            <button onclick="downloadAttachment('{{ public_url or '/uploads/' + ticket.filepath.split('/')[-1] }}', '{{ ticket.filepath.split('/')[-1] }}')"
                                    class="inline-flex items-center px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition font-medium">
                                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
                                </svg>
                                Download
                            </button>'''

if old_download_button in content:
    content = content.replace(old_download_button, new_download_button)
    
    # Add JavaScript function before endblock
    js_function = '''
<script>
// Force download of file from URL (works with cross-origin URLs)
async function downloadAttachment(url, filename) {
    try {
        // Fetch the file as a blob
        const response = await fetch(url);
        const blob = await response.blob();
        
        // Create a temporary link element
        const downloadUrl = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = downloadUrl;
        a.download = filename;
        document.body.appendChild(a);
        
        // Trigger download
        a.click();
        
        // Cleanup
        window.URL.revokeObjectURL(downloadUrl);
        document.body.removeChild(a);
        
        console.log('✅ File downloaded:', filename);
    } catch (error) {
        console.error('❌ Download failed:', error);
        // Fallback: open in new tab
        window.open(url, '_blank');
    }
}
</script>
{% endblock %}'''
    
    # Remove the old {% endblock %} and add our script
    content = content.replace('{% endblock %}', js_function)
    
    # Write back
    with open('templates/view_ticket.html', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ Fixed download button with JavaScript force-download!")
else:
    print("❌ Could not find download button to update")
