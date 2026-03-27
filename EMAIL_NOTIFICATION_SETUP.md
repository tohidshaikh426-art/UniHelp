# Email Notification Setup Guide

## Overview
This guide shows how to add email notifications for ticket creation and resolution in UniHelp.

## Files Created
✅ `email_notifications.py` - Already created with email functions

## Changes Needed in app.py

### 1. Add Import (Line ~17)
After the line `from file_uploads import file_uploads`, add:
```python
from email_notifications import send_ticket_created_email, send_ticket_resolved_email
```

### 2. Update create_ticket() Function (Around line 863-882)
Replace this section:
```python
if new_ticket:
    ticket_id = new_ticket['ticketid']
    
    # Auto-assign ticket to available technician
    all_users = db.get_all_users()
    technicians = [u for u in all_users if u['role'] == 'technician' and u['isapproved']]
    
    assigned_technician = None
    if technicians:
        # Simple assignment - assign to first available technician
        assigned_technician = technicians[0]
        db.update_ticket(ticket_id, {
            'assignedto': assigned_technician['userid'],
            'status': 'In Progress'
        })
    
    if assigned_technician:
        flash(f'Ticket created and assigned to {assigned_technician["name"]}', 'success')
    else:
        flash('Ticket created successfully. A technician will be assigned soon.', 'success')
```

With this:
```python
if new_ticket:
    ticket_id = new_ticket['ticketid']
    
    # Get user info for email
    user_info = db.get_user_by_id(session.get('user_id'))
    user_email = user_info.get('email', '') if user_info else ''
    user_name = user_info.get('name', 'User') if user_info else 'User'
    
    # Auto-assign ticket to available technician
    all_users = db.get_all_users()
    technicians = [u for u in all_users if u['role'] == 'technician' and u['isapproved']]
    
    assigned_technician = None
    if technicians:
        # Simple assignment - assign to first available technician
        assigned_technician = technicians[0]
        db.update_ticket(ticket_id, {
            'assignedto': assigned_technician['userid'],
            'status': 'In Progress'
        })
    
    # Send email notification
    if user_email:
        try:
            send_ticket_created_email(
                app=app,
                mail=mail,
                ticket_id=ticket_id,
                user_email=user_email,
                user_name=user_name,
                ticket_title=title,
                issue_description=description,
                technician_name=assigned_technician['name'] if assigned_technician else None
            )
        except Exception as e:
            print(f"Email send failed: {e}")
    
    if assigned_technician:
        flash(f'Ticket created and assigned to {assigned_technician["name"]}', 'success')
    else:
        flash('Ticket created successfully. A technician will be assigned soon.', 'success')
```

### 3. Update update_ticket() Function (Around line 703-743)
Add email sending when ticket is resolved/closed. After this line:
```python
db.update_ticket(ticket_id, update_data)
```

Add this code:
```python
# Send email notification if ticket is being resolved/closed
if status in ['Resolved', 'Closed']:
    try:
        # Get ticket owner's info
        ticket_owner = db.get_user_by_id(ticket.get('userid'))
        if ticket_owner and ticket_owner.get('email'):
            send_ticket_resolved_email(
                app=app,
                mail=mail,
                ticket_id=ticket_id,
                user_email=ticket_owner['email'],
                user_name=ticket_owner.get('name', 'User'),
                ticket_title=ticket.get('title', f'Ticket #{ticket_id}'),
                resolution_notes=resolution_notes
            )
    except Exception as e:
        print(f"Resolution email send failed: {e}")
```

## Configuration Required

### Update .env file
Make sure these are configured:
```env
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### For Gmail:
1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Generate an App Password: https://myaccount.google.com/apppasswords
4. Use that 16-character password in MAIL_PASSWORD

## Testing

1. Create a new ticket
   - Check your email inbox
   - Should receive "Ticket Created Successfully" email
   
2. Resolve a ticket (as technician)
   - Check email inbox
   - Should receive "Ticket Resolved" email

## Email Features

### Ticket Creation Email Includes:
- ✅ Ticket ID
- ✅ Issue title
- ✅ Description
- ✅ Assigned technician name (if assigned)
- ✅ Professional formatting

### Ticket Resolution Email Includes:
- ✅ Ticket ID
- ✅ Issue title
- ✅ Resolution notes
- ✅ Professional formatting
- ✅ Next steps information

## Error Handling
- If email is not configured, system logs warning but continues
- If email fails to send, error is logged but ticket operation succeeds
- No user-facing errors shown for email failures
