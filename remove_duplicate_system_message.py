#!/usr/bin/env python3
"""Remove the duplicate system message from admin_send_direct_message"""

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the system message block
old_code = """        # Send initial system message
        db.create_chat_message({
            'sessionid': session_id,
            'sender': 'system',
            'message': f'📢 Direct message from Admin {admin_name}',
            'intent': 'system'
        })
        
        # Send admin's message
        db.create_chat_message({"""

new_code = """        # Send admin's message only (no system message)
        db.create_chat_message({"""

if old_code not in content:
    print("❌ Could not find the code pattern to replace!")
    exit(1)

new_content = content.replace(old_code, new_code)

# Write back to app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Successfully removed duplicate system message")
