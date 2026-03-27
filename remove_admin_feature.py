#!/usr/bin/env python3
"""Remove admin live chat monitoring feature"""

print("Removing admin live chat feature...")

# 1. Remove navigation link from base.html
print("\n📝 Removing 'Monitor Live Chats' link from base.html...")
with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Desktop navigation - remove the link
old_nav = '''                                <a href="{{ url_for('admin_technicians') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    💬 Chat with Technicians
                                </a>
                                <a href="{{ url_for('admin_live_chats') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    📱 Monitor Live Chats
                                </a>
                                <a href="{{ url_for('chatbot') }}"'''

new_nav = '''                                <a href="{{ url_for('admin_technicians') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    💬 Chat with Technicians
                                </a>
                                <a href="{{ url_for('chatbot') }}"'''

if old_nav in content:
    content = content.replace(old_nav, new_nav)
    print("✅ Removed from desktop navigation")
else:
    print("⚠️  Desktop nav pattern not found (already removed?)")

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

# 2. Remove routes from app.py
print("\n📝 Removing admin live chat routes from app.py...")
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove the admin_live_chats route
start_marker = "@app.route('/admin/live_chats')"
end_marker = "@app.route('/admin/chat/<int:live_chat_id>')"

start_pos = content.find(start_marker)
if start_pos != -1:
    # Find the end of admin_view_chat function
    end_pos = content.find(end_marker)
    if end_pos != -1:
        # Remove both routes
        next_route = "@app.route('/chatbot')\n@app.route('/ai-chat')"
        next_pos = content.find(next_route)
        
        if next_pos != -1:
            # Remove everything from admin_live_chats to just before /chatbot
            content = content[:start_pos] + content[next_pos:]
            print("✅ Removed admin_live_chats route")
            print("✅ Removed admin_view_chat route")
        else:
            print("❌ Could not find end point")
    else:
        print("❌ Could not find admin_view_chat route")
else:
    print("⚠️  admin_live_chats route not found (already removed?)")

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("\n✅ Feature removal complete!")
print("\nNote: Template files still exist but won't be accessible:")
print("  - templates/admin/live_chats.html")
print("  - templates/admin/chat_view.html")
print("\nYou can delete them manually if desired.")
