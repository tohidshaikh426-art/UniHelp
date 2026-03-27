#!/usr/bin/env python3
"""
Universal File Modifier - Reliable alternative to search_replace
Usage: python modify_file.py

This tool provides a simple and reliable way to modify files without complex pattern matching.
It uses exact string matching and provides clear feedback on what was changed.
"""

import os
import shutil
from datetime import datetime

def backup_file(filepath):
    """Create a backup of the file"""
    if os.path.exists(filepath):
        backup_path = f"{filepath}.backup"
        shutil.copy2(filepath, backup_path)
        print(f"✅ Created backup: {backup_path}")

def read_file(filepath):
    """Read file content"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ File not found: {filepath}")
        return None

def write_file(filepath, content):
    """Write content to file"""
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ Saved: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error writing file: {e}")
        return False

def replace_text(content, old, new, description="", allow_multiple=False):
    """Replace text in content - EXACT MATCH ONLY
    
    Args:
        content: File content
        old: Text to find (must match exactly including whitespace)
        new: Replacement text
        description: Optional description for logging
        allow_multiple: If True, replaces all occurrences. If False, only replaces if exactly one match found.
    
    Returns:
        Modified content or original if no match found
    """
    count = content.count(old)
    
    if count == 0:
        print(f"⚠️  Text NOT found")
        print(f"   Search term: {old[:100]}..." if len(old) > 100 else f"   Search term: {old}")
        print(f"   Tip: Make sure the text matches EXACTLY (including whitespace, indentation, and line breaks)")
        print(f"   Tip: Use replace_all() if you expect multiple occurrences")
        return content
    elif count > 1 and not allow_multiple:
        print(f"⚠️  Text found {count} times but allow_multiple=False")
        print(f"   Found multiple occurrences. To replace all, use replace_all() or set allow_multiple=True")
        print(f"   Search term: {old[:100]}..." if len(old) > 100 else f"   Search term: {old}")
        return content
    else:
        # Replace all occurrences (whether count == 1 or count > 1 with allow_multiple=True)
        content = content.replace(old, new)
        print(f"✅ Replaced {count} occurrence(s): {description or 'Text replacement'}")
        return content

def insert_after_marker(content, marker, text_to_insert, strict=True):
    """Insert text after a specific marker string
    
    Args:
        content: File content
        marker: Text to search for (must match exactly)
        text_to_insert: Text to insert after the marker
        strict: If True, returns error if marker not found. If False, appends to end.
    
    Returns:
        Modified content or original if marker not found (when strict=False)
    """
    pos = content.find(marker)
    if pos != -1:
        insert_pos = pos + len(marker)
        content = content[:insert_pos] + "\n" + text_to_insert + content[insert_pos:]
        print(f"✅ Inserted after marker: {marker[:50]}...")
        return content
    else:
        action = "Returning original content" if strict else "Appending to end of file"
        print(f"⚠️  Marker not found: {marker[:50]}...")
        print(f"   {action}")
        if not strict:
            content = content + "\n" + text_to_insert
            print(f"✅ Appended to end of file")
        return content

def insert_before_marker(content, marker, text_to_insert, strict=True):
    """Insert text before a specific marker string
    
    Args:
        content: File content
        marker: Text to search for (must match exactly)
        text_to_insert: Text to insert before the marker
        strict: If True, returns error if marker not found. If False, appends to end.
    
    Returns:
        Modified content or original if marker not found (when strict=False)
    """
    pos = content.find(marker)
    if pos != -1:
        content = content[:pos] + text_to_insert + "\n" + content[pos:]
        print(f"✅ Inserted before marker: {marker[:50]}...")
        return content
    else:
        action = "Returning original content" if strict else "Appending to end of file"
        print(f"⚠️  Marker not found: {marker[:50]}...")
        print(f"   {action}")
        if not strict:
            content = content + "\n" + text_to_insert
            print(f"✅ Appended to end of file")
        return content

def replace_all(content, old, new, description="", min_replacements=1):
    """Replace ALL occurrences of text in content
    
    Args:
        content: File content
        old: Text to find (must match exactly)
        new: Replacement text
        description: Optional description for logging
        min_replacements: Minimum expected replacements (default 1). Warns if fewer found.
    
    Returns:
        Modified content or original if no match found
    """
    count = content.count(old)
    
    if count == 0:
        print(f"⚠️  Text NOT found")
        print(f"   Search term: {old[:100]}..." if len(old) > 100 else f"   Search term: {old}")
        print(f"   Tip: Verify the text exists in the file")
        return content
    
    if count < min_replacements:
        print(f"⚠️  Found {count} occurrence(s), expected at least {min_replacements}")
        print(f"   Search term: {old[:100]}..." if len(old) > 100 else f"   Search term: {old}")
    
    content = content.replace(old, new)
    print(f"✅ Replaced all {count} occurrence(s): {description or 'Text replacement'}")
    return content

def find_and_replace_regex(content, pattern, new, description=""):
    """Find and replace using regex pattern (for advanced users)"""
    import re
    try:
        matches = re.findall(pattern, content, re.MULTILINE)
        if not matches:
            print(f"⚠️  Pattern NOT found: {pattern[:50]}...")
            return content
        
        content = re.sub(pattern, new, content, flags=re.MULTILINE)
        print(f"✅ Replaced {len(matches)} matches: {description or pattern[:50]}")
        return content
    except re.error as e:
        print(f"❌ Invalid regex pattern: {e}")
        return content

# ============================================================================
# EXAMPLE USAGE - Customize this section for your needs
# ============================================================================

def main():
    """Main modification logic"""
    
    print("=" * 60)
    print("File Modification Script")
    print("=" * 60)
    print("\n📖 HOW TO USE THIS TOOL:")
    print("1. Read the file you want to modify")
    print("2. Create backup (automatic)")
    print("3. Use replace_text() for exact matches")
    print("4. Use replace_all() for multiple occurrences")
    print("5. Use insert_after/before_marker() for additions")
    print("6. Write the modified content back")
    print("=" * 60)
    
    # Example 1: Simple text replacement
    print("\n📝 Example 1: Replace text in base.html")
    filepath = 'templates/base.html'
    content = read_file(filepath)
    
    if content:
        # Backup first
        backup_file(filepath)
        
        # Make changes
        old_text = '''<a href="{{ url_for('admin_technicians') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    💬 Chat with Technicians
                                </a>'''
        
        new_text = '''<a href="{{ url_for('admin_technicians') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    💬 Chat with Technicians
                                </a>
                                <a href="{{ url_for('admin_live_chats') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    📱 Monitor Live Chats
                                </a>'''
        
        content = replace_text(content, old_text, new_text, "Add live chats link")
        write_file(filepath, content)
    
    # Example 2: Insert code at specific location
    print("\n📝 Example 2: Insert routes in app.py")
    filepath = 'app.py'
    content = read_file(filepath)
    
    if content:
        backup_file(filepath)
        
        # Find where to insert
        marker = "@app.route('/chatbot')"
        new_routes = """
@app.route('/new/route')
def new_route():
    return 'New route!'
"""
        content = insert_before_marker(content, marker, new_routes)
        write_file(filepath, content)
    
    print("\n" + "=" * 60)
    print("✅ All modifications complete!")
    print("=" * 60)

if __name__ == '__main__':
    main()
