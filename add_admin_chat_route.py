#!/usr/bin/env python3
"""Add admin chat view route to app.py"""

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new route
new_route = """
@app.route('/admin/chat/<int:session_id>')
@login_required
@role_required(['admin'])
def admin_chat_view(session_id):
    \"\"\"Admin chat view for live messaging with technician\"\"\"
    
    try:
        if not db.client:
            return "Database connection not available", 500
        
        # Get chat session
        session_data = db.get_chat_session_by_id(session_id)
        if not session_data:
            return "Chat session not found", 404
        
        # Verify this session belongs to current admin
        if session_data['userid'] != session.get('user_id'):
            return "Unauthorized", 403
        
        # Get technician info from live_chat
        live_chat_response = db.client.table('live_chat').select('*')\
            .eq('sessionid', session_id)\
            .execute()
        
        if not live_chat_response.data:
            return "Live chat not found", 404
        
        live_chat = live_chat_response.data[0]
        technician_id = live_chat['technicianid']
        
        # Get technician details
        technician = db.get_user_by_id(technician_id)
        if not technician:
            return "Technician not found", 404
        
        # Get all messages from this session
        response = db.client.table('chat_message').select('*')\
            .eq('sessionid', session_id)\
            .order('created_at', desc=False)\
            .execute()
        
        messages = response.data if response.data else []
        
        return render_template('admin/chat_view.html',
                             session_id=session_id,
                             technician_name=technician['name'],
                             technician_email=technician['email'],
                             messages=messages)
    
    except Exception as e:
        print(f"❌ Error in admin chat view: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return "Internal server error", 500

"""

# Find insertion point (after admin_send_direct_message function)
# Look for the next @app.route after admin_send_direct_message
insertion_marker = "@app.route('/admin/send_direct_message', methods=['POST'])"
insertion_point = content.find(insertion_marker)

if insertion_point == -1:
    print("❌ Could not find insertion marker!")
    exit(1)

# Find the end of the admin_send_direct_message function
# Look for the next @app.route or end of file
next_route_pattern = "\n@app.route('"
next_route_point = content.find(next_route_pattern, insertion_point + len(insertion_marker))

if next_route_point == -1:
    # If no next route, insert at end of file
    insert_position = len(content)
else:
    # Insert before the next route
    insert_position = next_route_point

new_content = content[:insert_position] + "\n" + new_route + content[insert_position:]

# Write back to app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Successfully added admin chat view route to app.py")
