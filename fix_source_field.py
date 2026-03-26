#!/usr/bin/env python3
"""Remove the 'source' field from chat_session creation in app.py"""

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Remove the source line
old_code = """        chat_session = db.create_chat_session({
            'userid': admin_id,
            'status': 'active',
            'source': 'admin_direct_message'
        })"""

new_code = """        chat_session = db.create_chat_session({
            'userid': admin_id,
            'status': 'active'
        })"""

if old_code not in content:
    print("❌ Could not find the code pattern to replace!")
    exit(1)

new_content = content.replace(old_code, new_code)

# Write back to app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Successfully removed 'source' field from chat_session creation")
