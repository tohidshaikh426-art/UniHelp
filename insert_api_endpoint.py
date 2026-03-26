#!/usr/bin/env python3
"""Insert get_available_technicians API endpoint into app.py"""

# Read app.py
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Define the new API endpoint
new_api = """
@app.route('/api/admin/get_available_technicians')
@login_required
@role_required(['admin'])
def get_available_technicians():
    \"\"\"Get list of available technicians for live chat\"\"\"
    
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        # Get all approved technicians with their presence status
        response = db.client.table('user').select('''
            userid, name, email,
            user_presence(status, last_seen)
        ''').eq('role', 'technician').eq('isapproved', True).execute()
        
        technicians = response.data if response.data else []
        
        # Filter to only online/available technicians
        available_technicians = []
        for tech in technicians:
            presence = tech.get('user_presence')
            # Include technician if they're online or have recent activity
            if presence and presence.get('status') == 'online':
                available_technicians.append({
                    'userid': tech['userid'],
                    'name': tech['name'],
                    'email': tech['email']
                })
        
        print(f"✅ Found {len(available_technicians)} available technicians")
        
        return jsonify({
            'success': True,
            'technicians': available_technicians,
            'count': len(available_technicians)
        })
    
    except Exception as e:
        print(f"❌ Error getting available technicians: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to get technicians: {str(e)}'}), 500

"""

# Find the insertion point (before admin/send_direct_message)
insertion_marker = "# ==================== ADMIN DIRECT MESSAGING ===================="
insertion_point = content.find(insertion_marker)

if insertion_point == -1:
    print("❌ Could not find insertion marker!")
    exit(1)

# Find the end of the marker line
end_of_line = content.find('\n', insertion_point)
if end_of_line == -1:
    print("❌ Could not find end of line!")
    exit(1)

# Insert after the marker line with two newlines
insert_position = end_of_line + 1
new_content = content[:insert_position] + "\n" + new_api + content[insert_position:]

# Write back to app.py
with open('app.py', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("✅ Successfully added get_available_technicians API endpoint to app.py")
print("📍 Inserted at line:", content[:insert_position].count('\n') + 1)
