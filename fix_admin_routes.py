#!/usr/bin/env python3
"""Fix admin navigation and add live chat routes"""

# Fix base.html - Add live chats link
print("Updating templates/base.html...")
with open('templates/base.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Desktop navigation
old_nav = '''                                <a href="{{ url_for('admin_technicians') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    💬 Chat with Technicians
                                </a>
                                <a href="{{ url_for('chatbot') }}"'''

new_nav = '''                                <a href="{{ url_for('admin_technicians') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    💬 Chat with Technicians
                                </a>
                                <a href="{{ url_for('admin_live_chats') }}" 
                                   class="text-gray-700 hover:bg-gray-100 hover:text-primary px-3 py-2 rounded-md text-sm font-medium transition">
                                    📱 Monitor Live Chats
                                </a>
                                <a href="{{ url_for('chatbot') }}"'''

content = content.replace(old_nav, new_nav)

with open('templates/base.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Updated templates/base.html")

# Now add routes to app.py
print("\nAdding admin routes to app.py...")
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the location before /chatbot route
insert_point = content.find("@app.route('/chatbot')\n@app.route('/ai-chat')")

if insert_point == -1:
    print("❌ Could not find insertion point!")
    exit(1)

admin_routes = '''@app.route('/admin/live_chats')
@login_required
@role_required(['admin'])
def admin_live_chats():
    """Admin view of all active live chats"""
    try:
        if not db.client:
            flash('Database connection not available', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get all active live chats
        response = db.client.table('live_chat').select('*')\\
            .eq('status', 'active')\\
            .execute()
        
        live_chats = []
        if response.data:
            for chat in response.data:
                chat_info = {
                    'livechatid': chat['livechatid'],
                    'sessionid': chat['sessionid'],
                    'technicianid': chat['technicianid'],
                    'started_at': chat.get('started_at'),
                    'technician_name': 'Unknown',
                    'user_name': 'Unknown',
                    'user_email': '',
                    'last_message': ''
                }
                
                # Get technician name
                tech_response = db.client.table('technician').select('name').eq('technicianid', chat['technicianid']).execute()
                if tech_response.data and len(tech_response.data) > 0:
                    chat_info['technician_name'] = tech_response.data[0]['name']
                
                # Get session and user info
                session_response = db.client.table('chat_session').select('userid').eq('sessionid', chat['sessionid']).execute()
                if session_response.data and len(session_response.data) > 0:
                    user_id = session_response.data[0]['userid']
                    
                    # Get user details
                    user_response = db.client.table('user').select('name, email').eq('userid', user_id).execute()
                    if user_response.data and len(user_response.data) > 0:
                        user_data = user_response.data[0]
                        chat_info['user_name'] = user_data['name']
                        chat_info['user_email'] = user_data['email']
                    
                    # Get last message
                    msg_response = db.client.table('chat_message').select('message').eq('sessionid', chat['sessionid']).order('created_at', desc=True).limit(1).execute()
                    if msg_response.data and len(msg_response.data) > 0:
                        chat_info['last_message'] = msg_response.data[0]['message']
                
                live_chats.append(chat_info)
        
        return render_template('admin/live_chats.html', live_chats=live_chats)
    
    except Exception as e:
        print(f"❌ Error loading admin live chats: {e}")
        flash('Failed to load live chats', 'error')
        return redirect(url_for('admin_dashboard'))


@app.route('/admin/chat/<int:live_chat_id>')
@login_required
@role_required(['admin'])
def admin_view_chat(live_chat_id):
    """Admin view specific chat details and messages"""
    try:
        if not db.client:
            flash('Database connection not available', 'error')
            return redirect(url_for('admin_live_chats'))
        
        # Get live chat details
        response = db.client.table('live_chat').select('*')\\
            .eq('livechatid', live_chat_id)\\
            .execute()
        
        if not response.data or len(response.data) == 0:
            flash('Live chat not found', 'error')
            return redirect(url_for('admin_live_chats'))
        
        live_chat = response.data[0]
        
        # Get session and user info
        session_response = db.client.table('chat_session').select('userid')\\
            .eq('sessionid', live_chat['sessionid'])\\
            .execute()
        
        user_name = 'Unknown'
        user_email = ''
        technician_name = 'Unknown'
        
        if session_response.data and len(session_response.data) > 0:
            user_id = session_response.data[0]['userid']
            
            # Get user details
            user_response = db.client.table('user').select('name, email')\\
                .eq('userid', user_id)\\
                .execute()
            
            if user_response.data and len(user_response.data) > 0:
                user_data = user_response.data[0]
                user_name = user_data['name']
                user_email = user_data['email']
        
        # Get technician name
        tech_response = db.client.table('technician').select('name')\\
            .eq('technicianid', live_chat['technicianid'])\\
            .execute()
        
        if tech_response.data and len(tech_response.data) > 0:
            technician_name = tech_response.data[0]['name']
        
        # Get chat messages
        msg_response = db.client.table('chat_message').select('*')\\
            .eq('sessionid', live_chat['sessionid'])\\
            .order('created_at', desc=False)\\
            .execute()
        
        messages = msg_response.data if msg_response.data else []
        
        return render_template('admin/chat_view.html', 
                             live_chat=live_chat,
                             messages=messages,
                             user_name=user_name,
                             user_email=user_email,
                             technician_name=technician_name)
    
    except Exception as e:
        print(f"❌ Error viewing admin chat: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash('Failed to load chat', 'error')
        return redirect(url_for('admin_live_chats'))


'''

# Insert the routes
content = content[:insert_point] + admin_routes + content[insert_point:]

with open('app.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Added admin routes to app.py")
print("\n✅ All updates complete!")
