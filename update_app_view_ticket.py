# Update app.py to add public_url for ticket attachments
with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the authorization check section and add public_url generation after it
old_code = '''        if not is_admin and not is_creator and not is_assignee:
            flash('Access denied', 'error')
            return redirect(url_for('dashboard'))
        
        # NEW: Only fetch comments for staff, technicians, and admin (NOT students)'''

new_code = '''        if not is_admin and not is_creator and not is_assignee:
            flash('Access denied', 'error')
            return redirect(url_for('dashboard'))
        
        # Generate public URL for attachment if filepath exists
        public_url = None
        if ticket.get('filepath'):
            filepath = ticket['filepath']
            if filepath.startswith('supabase://'):
                # Extract bucket and path from supabase:// format
                parts = filepath.replace('supabase://', '').split('/', 1)
                if len(parts) == 2:
                    bucket_name = parts[0]
                    file_path_in_bucket = parts[1]
                    try:
                        public_url = db.client.storage.from_(bucket_name).get_public_url(file_path_in_bucket)
                        print(f"🔗 Generated public URL for ticket {ticket_id}: {public_url}")
                    except Exception as url_error:
                        print(f"⚠️ Error generating public URL: {url_error}")
                        public_url = None
        
        # NEW: Only fetch comments for staff, technicians, and admin (NOT students)'''

if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Also update the render_template call to include public_url
    old_render = '''return render_template('view_ticket.html', 
                             ticket=ticket, 
                             comments=comments,
                             can_comment=can_comment,
                             active_session=active_session)'''
    
    new_render = '''return render_template('view_ticket.html', 
                             ticket=ticket, 
                             public_url=public_url,
                             comments=comments,
                             can_comment=can_comment,
                             active_session=active_session)'''
    
    content = content.replace(old_render, new_render)
    
    # Write back
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("✅ app.py updated with public URL generation for ticket attachments!")
else:
    print("❌ Could not find code section to update")
