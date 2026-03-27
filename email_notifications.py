"""
Email Notification Functions for UniHelp
Send automated emails for ticket creation and resolution
"""

from flask_mail import Message


def send_ticket_created_email(app, mail, ticket_id, user_email, user_name, ticket_title, issue_description, technician_name=None):
    """Send email notification when ticket is created"""
    try:
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            print(f"⚠️ Email not configured - skipping notification for ticket {ticket_id}")
            return False
        
        subject = f"✅ Ticket Created: {ticket_title} (#{ticket_id})"
        
        # Build email content
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb;">Ticket Created Successfully</h2>
                
                <p>Dear {user_name},</p>
                
                <p>Your support ticket has been created successfully.</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1f2937; margin-top: 0;">Ticket Details:</h3>
                    <p><strong>Ticket ID:</strong> #{ticket_id}</p>
                    <p><strong>Issue:</strong> {ticket_title}</p>
                    <p><strong>Description:</strong></p>
                    <p style="background-color: white; padding: 10px; border-left: 3px solid #2563eb;">{issue_description}</p>
        """
        
        if technician_name:
            html_body += f"""
                    <p><strong>Assigned Technician:</strong> {technician_name}</p>
            """
        else:
            html_body += """
                    <p><strong>Status:</strong> A technician will be assigned shortly</p>
            """
        
        html_body += """
                </div>
                
                <p>Our IT support team will review your request and get back to you as soon as possible.</p>
                
                <p>You can track your ticket status by logging into your dashboard.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>UniHelp IT Support Team</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin-top: 30px;">
                <p style="font-size: 12px; color: #6b7280;">This is an automated message. Please do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body
        )
        
        mail.send(msg)
        print(f"✅ Ticket created email sent to {user_email} for ticket #{ticket_id}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send ticket created email: {e}")
        return False


def send_ticket_resolved_email(app, mail, ticket_id, user_email, user_name, ticket_title, resolution_notes=None):
    """Send email notification when ticket is resolved/closed"""
    try:
        if not app.config.get('MAIL_USERNAME') or not app.config.get('MAIL_PASSWORD'):
            print(f"⚠️ Email not configured - skipping notification for ticket {ticket_id}")
            return False
        
        subject = f"🎉 Ticket Resolved: {ticket_title} (#{ticket_id})"
        
        html_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #10b981;">Ticket Resolved</h2>
                
                <p>Dear {user_name},</p>
                
                <p>Great news! Your support ticket has been resolved.</p>
                
                <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="color: #1f2937; margin-top: 0;">Ticket Summary:</h3>
                    <p><strong>Ticket ID:</strong> #{ticket_id}</p>
                    <p><strong>Issue:</strong> {ticket_title}</p>
        """
        
        if resolution_notes:
            html_body += f"""
                    <p><strong>Resolution:</strong></p>
                    <p style="background-color: white; padding: 10px; border-left: 3px solid #10b981;">{resolution_notes}</p>
            """
        
        html_body += """
                </div>
                
                <p>If you're satisfied with the resolution, no further action is needed.</p>
                
                <p>If you still have issues, please don't hesitate to create a new ticket or contact our support team.</p>
                
                <p style="margin-top: 30px;">
                    Best regards,<br>
                    <strong>UniHelp IT Support Team</strong>
                </p>
                
                <hr style="border: none; border-top: 1px solid #e5e7eb; margin-top: 30px;">
                <p style="font-size: 12px; color: #6b7280;">This is an automated message. Please do not reply.</p>
            </div>
        </body>
        </html>
        """
        
        msg = Message(
            subject=subject,
            recipients=[user_email],
            html=html_body
        )
        
        mail.send(msg)
        print(f"✅ Ticket resolved email sent to {user_email} for ticket #{ticket_id}")
        return True
        
    except Exception as e:
        print(f"❌ Failed to send ticket resolved email: {e}")
        return False
