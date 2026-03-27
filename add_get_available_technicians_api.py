"""
Add API endpoint for getting available technicians
Insert this code into app.py before line 1584 (before @app.route('/admin/send_direct_message'))
"""

# Copy this entire function and paste it in app.py at line 1582 (after the comment "# ==================== ADMIN DIRECT MESSAGING ====================")

@app.route('/api/admin/get_available_technicians')
@login_required
@role_required(['admin'])
def get_available_technicians():
    """Get list of available technicians for live chat"""
    
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
