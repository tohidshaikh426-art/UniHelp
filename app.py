# app.py
# UniHelp IT Helpdesk Management System
# Main Flask Application with Role-Based Permissions
from dotenv import load_dotenv
import google.generativeai as genai
import google.generativeai.types as types
load_dotenv()
from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from supabase_client import db
import os
from datetime import datetime, timedelta
from functools import wraps
import re
from difflib import SequenceMatcher

# NEW: Import Flask-Mail for email notifications
from flask_mail import Mail, Message

# AI Chatbot Integration
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel('gemini-1.5-pro')
        AI_ENABLED = True
        print("✅ Gemini AI Enabled and Model Loaded")
    except Exception as e:
        AI_ENABLED = False
        print(f"❌ Gemini AI Setup Failed: {e}")
else:
    AI_ENABLED = False
    print("⚠️  Gemini API key not found. Using fallback mode.")


app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'fallback-secret-key-change-in-production')
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'doc', 'docx'}

# NEW: Flask-Mail configuration (update with your SMTP details)
app.config['MAIL_SERVER'] = 'smtp.gmail.com'  # Example: Gmail SMTP
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME', 'unihelp.project@gmail.com')  # Replace with your email
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD', 'bfuz ktgu xxdp zuvv')  # Use app password for Gmail
app.config['MAIL_DEFAULT_SENDER'] = os.getenv('MAIL_USERNAME', 'your-email@gmail.com')

# NEW: Initialize Flask-Mail
mail = Mail(app)

# Database helper functions
def get_db_connection():
    """Return the Supabase client"""
    return db


def update_user_presence():
    """Update user presence to show they're online"""
    if 'user_id' not in session:
        return
    
    try:
        user_id = session['user_id']
        now = datetime.now().isoformat()
        
        # Try to update existing presence record
        existing = db.client.table('user_presence').select('*').eq('userid', user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing record
            db.client.table('user_presence').update({
                'status': 'online',
                'last_seen': now
            }).eq('userid', user_id).execute()
        else:
            # Insert new record
            db.client.table('user_presence').insert({
                'userid': user_id,
                'status': 'online',
                'last_seen': now
            }).execute()
            
        print(f"✅ Updated presence for user {user_id}")
    except Exception as e:
        print(f"⚠️  Failed to update presence: {e}")
        # Don't fail the request if presence update fails

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.before_request
def before_request():
    """Update user presence before processing any request (except static files)"""
    if request.endpoint and request.endpoint != 'static':
        update_user_presence()

# Authentication decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'role' not in session or session['role'] not in roles:
                flash('Access denied. Insufficient permissions.', 'error')
                return redirect(url_for('dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator



# ==================== PUBLIC ROUTES ====================

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']  # Plain password for email
        role = request.form['role']
        
        if role not in ['staff', 'technician', 'student']:
            flash('Invalid role selected', 'error')
            return redirect(url_for('register'))
        
        # NEW: Send email after registration (before hashing, so we can include plain password in approval email)
        msg = Message('Registration Pending Approval', recipients=[email])
        msg.body = f"Hello {name},\n\nThank you for registering with UniHelp. Please wait for admin approval before you can log in.\n\nBest regards,\nUniHelp Team"
        mail.send(msg)
        
        password_hash = generate_password_hash(password)
        
        try:
            new_user = db.create_user({
                'name': name,
                'email': email,
                'passwordhash': password_hash,
                'role': role,
                'isapproved': False
            })
            if new_user:
                flash('Registration successful! Please wait for admin approval.', 'success')
                return redirect(url_for('login'))
            else:
                flash('Failed to create user', 'error')
        except Exception as e:
            if 'UNIQUE constraint' in str(e) or 'email' in str(e).lower():
                flash('Email already registered', 'error')
            else:
                flash(f'Registration failed: {str(e)}', 'error')
    
    return render_template('register.html')

@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        
        user = db.get_user_by_email(email)
        
        if user and check_password_hash(user['passwordhash'], password):
            if not user['isapproved']:
                flash('Your account is pending approval from admin', 'warning')
                return redirect(url_for('login'))
            
            # IMPORTANT: Set all session variables
            session['user_id'] = user['userid']
            session['name'] = user['name']
            session['email'] = user['email']
            session['role'] = user['role']  # Make sure this is set!
            
            flash(f'Welcome back, {user["name"]}!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials', 'error')
    
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'success')
    return redirect(url_for('login'))


# ==================== PASSWORD RESET ROUTES ====================

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    """Handle forgot password requests"""
    if request.method == 'POST':
        email = request.form['email'].strip().lower()
        
        # Validate email format
        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            flash('Please enter a valid email address', 'error')
            return render_template('forgot_password.html')
        
        # Check if user exists
        user = db.get_user_by_email(email)
        
        if not user:
            # Don't reveal if email exists or not (security best practice)
            flash('If that email is registered, a password reset link has been sent.', 'info')
            return render_template('forgot_password.html')
        
        # Generate secure token
        import secrets
        token = secrets.token_urlsafe(32)  # 256-bit token
        
        # Set expiration time (1 hour from now)
        expires_at = datetime.now() + timedelta(hours=1)
        
        # Delete any expired tokens for this email first
        db.delete_expired_tokens(email)
        
        # Create new token
        token_data = {
            'email': email,
            'token': token,
            'expires_at': expires_at.isoformat(),
            'used': False
        }
        
        result = db.create_password_reset_token(token_data)
        
        if result:
            # Send reset email
            try:
                reset_link = url_for('reset_password', token=token, _external=True)
                
                msg = Message(
                    subject='Password Reset Request - UniHelp',
                    recipients=[email],
                    html=f'''
                    <html>
                    <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
                        <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                            <h2 style="color: #2563eb;">Password Reset Request</h2>
                            <p>Hello {user['name']},</p>
                            <p>You requested to reset your password for your UniHelp account.</p>
                            <p style="margin: 30px 0;">
                                <a href="{reset_link}" 
                                   style="display: inline-block; background-color: #2563eb; color: white; 
                                          padding: 12px 30px; text-decoration: none; border-radius: 5px; 
                                          font-weight: bold;">
                                    Reset Password
                                </a>
                            </p>
                            <p><strong>This link will expire in 1 hour.</strong></p>
                            <p>If you didn't request this, please ignore this email and your password will remain unchanged.</p>
                            <hr style="margin: 30px 0; border: none; border-top: 1px solid #ddd;">
                            <p style="font-size: 14px; color: #666;">
                                Best regards,<br>
                                UniHelp IT Support Team
                            </p>
                        </div>
                    </body>
                    </html>
                    '''
                )
                
                mail.send(msg)
                print(f"✅ Password reset email sent to {email}")
                
            except Exception as e:
                print(f"❌ Failed to send reset email: {e}")
                flash('Failed to send reset email. Please try again later.', 'error')
                return render_template('forgot_password.html')
        
        flash('If that email is registered, a password reset link has been sent.', 'info')
    
    return render_template('forgot_password.html')


@app.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    """Handle password reset with token"""
    # Validate token
    reset_token = db.get_reset_token_by_token(token)
    
    if not reset_token:
        flash('Invalid or expired reset token. Please request a new password reset.', 'error')
        return redirect(url_for('forgot_password'))
    
    # Check if token is expired
    expires_at = datetime.fromisoformat(reset_token['expires_at'].replace('Z', '+00:00').replace('+00:00', ''))
    if datetime.now() > expires_at:
        flash('Reset token has expired. Please request a new password reset.', 'error')
        return redirect(url_for('forgot_password'))
    
    if request.method == 'POST':
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        
        # Validate password
        if len(password) < 8:
            flash('Password must be at least 8 characters long', 'error')
            return render_template('reset_password.html', token=token)
        
        if password != confirm_password:
            flash('Passwords do not match', 'error')
            return render_template('reset_password.html', token=token)
        
        # Get user
        user = db.get_user_by_email(reset_token['email'])
        
        if not user:
            flash('User not found', 'error')
            return redirect(url_for('forgot_password'))
        
        # Update password
        hashed_password = generate_password_hash(password)
        
        update_data = {'passwordhash': hashed_password}
        updated_user = db.update_user(user['userid'], update_data)
        
        if updated_user:
            # Mark token as used
            db.mark_token_as_used(token)
            
            flash('Your password has been successfully reset! You can now log in with your new password.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Failed to update password. Please try again.', 'error')
            return render_template('reset_password.html', token=token)
    
    return render_template('reset_password.html', token=token)

# ==================== DEBUG ROUTE (TEMPORARY) ====================
@app.route('/debug')
def debug():
    """Debug route to check Supabase connection"""
    import os
    from werkzeug.security import check_password_hash
    
    # Check raw environment variables
    supabase_url = os.getenv('SUPABASE_URL', 'NOT_SET')
    supabase_key = os.getenv('SUPABASE_KEY', 'NOT_SET')
    supabase_service_key = os.getenv('SUPABASE_SERVICE_KEY', 'NOT_SET')
    
    # Try to create Supabase client directly
    supabase_error = None
    supabase_test_success = False
    try:
        from supabase import create_client
        print("🔧 Attempting to create Supabase client...")
        test_client = create_client(supabase_url, supabase_key)
        print("✅ Direct Supabase client created!")
        supabase_test_success = True
        
        # Try to query admin user
        response = test_client.table('user').select('*').eq('email', 'admin@unihelp.com').execute()
        admin_data = response.data[0] if response.data else None
        print(f"Admin data: {admin_data}")
    except Exception as e:
        supabase_error = str(e)
        print(f"❌ Direct Supabase test failed: {supabase_error}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        admin_data = None
    
    password_ok = check_password_hash(admin_data['passwordhash'], 'admin123') if admin_data else False
    
    return {
        'admin_exists': admin_data is not None,
        'email': admin_data['email'] if admin_data else 'Not found',
        'is_approved': admin_data['isapproved'] if admin_data else False,
        'password_matches': password_ok,
        'direct_supabase_test': supabase_test_success,
        'supabase_error': supabase_error,
        'DEBUG_env_check': {
            'SUPABASE_URL_loaded': supabase_url != 'NOT_SET',
            'SUPABASE_URL_value': supabase_url[:40] + '...' if supabase_url != 'NOT_SET' else 'NOT_SET',
            'SUPABASE_KEY_loaded': supabase_key != 'NOT_SET',
            'SUPABASE_KEY_length': len(supabase_key) if supabase_key != 'NOT_SET' else 0,
            'SUPABASE_SERVICE_KEY_loaded': supabase_service_key != 'NOT_SET',
            'SUPABASE_SERVICE_KEY_length': len(supabase_service_key) if supabase_service_key != 'NOT_SET' else 0,
        }
    }

# ==================== DASHBOARD ====================

@app.route('/dashboard')
@login_required
def dashboard():
    role = session.get('role')
    
    if role == 'admin':
        return redirect(url_for('admin_dashboard'))
    elif role == 'technician':
        return redirect(url_for('technician_dashboard'))
    elif role in ['staff', 'student']:
        return redirect(url_for('user_dashboard'))
    
    return 'Invalid role', 403

# ==================== ADMIN ROUTES ====================

@app.route('/admin/dashboard')
@login_required
@role_required(['admin'])
def admin_dashboard():
    # Get statistics using Supabase
    all_users = db.get_all_users()
    all_tickets = db.get_all_tickets()
    
    total_users = len(all_users)
    pending_approvals = len([u for u in all_users if not u['isapproved']])
    total_tickets = len(all_tickets)
    open_tickets = len([t for t in all_tickets if t['status'] == 'Open'])
    in_progress = len([t for t in all_tickets if t['status'] == 'In Progress'])
    closed_tickets = len([t for t in all_tickets if t['status'] == 'Closed'])
    
    # Get recent tickets (already includes user info from Supabase query)
    recent_tickets = all_tickets[:10]
    
    stats = {
        'total_users': total_users,
        'pending_approvals': pending_approvals,
        'total_tickets': total_tickets,
        'open_tickets': open_tickets,
        'in_progress': in_progress,
        'closed_tickets': closed_tickets
    }
    
    return render_template('admin/dashboard.html', stats=stats, recent_tickets=recent_tickets)

@app.route('/admin/users')
@login_required
@role_required(['admin'])
def admin_users():
    """View and filter all users by role"""
    # Get filter parameter
    role_filter = request.args.get('role', 'all')
    
    # Get all users from Supabase
    all_users = db.get_all_users()
    
    # Filter users based on role
    if role_filter == 'all':
        users = all_users
    else:
        users = [u for u in all_users if u['role'] == role_filter]
    
    # Get statistics
    total_users = len(all_users)
    admin_count = len([u for u in all_users if u['role'] == 'admin'])
    tech_count = len([u for u in all_users if u['role'] == 'technician'])
    staff_count = len([u for u in all_users if u['role'] == 'staff'])
    student_count = len([u for u in all_users if u['role'] == 'student'])
    
    stats = {
        'total': total_users,
        'admins': admin_count,
        'technicians': tech_count,
        'staff': staff_count,
        'students': student_count
    }
    
    return render_template('admin/users.html', 
                         users=users, 
                         stats=stats,
                         current_filter=role_filter)


@app.route('/admin/approve_user/<int:user_id>')
@login_required
@role_required(['admin'])
def approve_user(user_id):
    # Get user details before approval
    user = db.get_user_by_id(user_id)
    
    if not user:
        flash('User not found', 'error')
        return redirect(url_for('admin_users'))
    
    db.update_user(user_id, {'isapproved': True})
    
    # NEW: Send congratulatory email with credentials (username and password)
    # Note: Since password is hashed, this sends username and a note to reset password. If you want plain password, store it temporarily (not recommended).
    msg = Message('Account Approved - Welcome to UniHelp!', recipients=[user['email']])
    msg.body = f"Congratulations {user['name']}!\n\nYour account has been approved by the admin. You can now log in.\n\nYour credentials:\nUsername: {user['email']}\nPassword: [Your registered password - if forgotten, use password reset]\n\nFor security, please change your password after first login.\n\nBest regards,\nUniHelp Team"
    mail.send(msg)
    
    flash('User approved successfully', 'success')
    return redirect(url_for('admin_users'))

@app.route('/admin/delete_user/<int:user_id>')
@login_required
@role_required(['admin'])
def delete_user(user_id):
    if user_id == session.get('user_id'):
        flash('Cannot delete your own account', 'error')
        return redirect(url_for('admin_users'))
    
    # Delete user from Supabase
    if db.client:
        response = db.client.table('user').delete().eq('userid', user_id).execute()
        if response.data:
            flash('User deleted successfully', 'success')
        else:
            flash('Failed to delete user', 'error')
    else:
        flash('Database connection not available', 'error')
    
    return redirect(url_for('admin_users'))

@app.route('/admin/tickets')
@login_required
@role_required(['admin'])
def admin_tickets():
    # Get all tickets from Supabase (includes user info)
    tickets = db.get_all_tickets()
    
    # Get all approved technicians
    all_users = db.get_all_users()
    technicians = [u for u in all_users if u['role'] == 'technician' and u['isapproved']]
    
    return render_template('admin/tickets.html', tickets=tickets, technicians=technicians)

@app.route('/admin/reassign_ticket/<int:ticket_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def reassign_ticket(ticket_id):
    """Manually reassign a ticket to a different technician"""
    new_technician_id = request.form.get('technician_id')
    
    if not new_technician_id:
        flash('Please select a technician', 'error')
        return redirect(url_for('admin_tickets'))
    
    # Check if technician exists and is approved
    technician = db.get_user_by_id(new_technician_id)
    
    if not technician or technician['role'] != 'technician' or not technician['isapproved']:
        flash('Invalid technician selected', 'error')
        return redirect(url_for('admin_tickets'))
    
    db.update_ticket(ticket_id, {'assignedto': new_technician_id, 'updatedat': datetime.now().isoformat()})
    
    flash(f'Ticket reassigned to {technician["name"]}', 'success')
    return redirect(url_for('admin_tickets'))

@app.route('/admin/auto_rebalance_tickets')
@login_required
@role_required(['admin'])
def auto_rebalance_tickets():
    """Rebalance unassigned tickets among available technicians"""
    # Get all tickets and filter for unassigned
    all_tickets = db.get_all_tickets()
    unassigned_tickets = [t for t in all_tickets if t['assignedto'] is None and t['status'] == 'Open']
    
    # Get approved technicians
    all_users = db.get_all_users()
    technicians = [u for u in all_users if u['role'] == 'technician' and u['isapproved']]
    
    reassigned_count = 0
    for ticket in unassigned_tickets:
        if technicians:
            # Simple round-robin assignment (you can improve this logic)
            technician = technicians[reassigned_count % len(technicians)]
            db.update_ticket(ticket['ticketid'], {
                'assignedto': technician['userid'],
                'status': 'In Progress',
                'updatedat': datetime.now().isoformat()
            })
            reassigned_count += 1
    
    flash(f'Rebalanced {reassigned_count} tickets among available technicians', 'success')
    return redirect(url_for('admin_tickets'))

@app.route('/admin/assign_ticket/<int:ticket_id>', methods=['POST'])
@login_required
@role_required(['admin'])
def assign_ticket(ticket_id):
    technician_id = request.form.get('technician_id')
    
    if not technician_id:
        flash('Please select a technician', 'error')
        return redirect(url_for('admin_tickets'))
    
    db.update_ticket(ticket_id, {
        'assignedto': technician_id,
        'status': 'In Progress',
        'updatedat': datetime.now().isoformat()
    })
    
    flash('Ticket assigned successfully', 'success')
    return redirect(url_for('admin_tickets'))

# ==================== TECHNICIAN ROUTES ====================

@app.route('/technician/dashboard')
@login_required
@role_required(['technician'])
def technician_dashboard():
    user_id = session.get('user_id')
    
    # Get assigned tickets from Supabase
    assigned_tickets = db.get_tickets_by_technician(user_id)
    
    # Get statistics
    total_assigned = len(assigned_tickets)
    in_progress = len([t for t in assigned_tickets if t['status'] == 'In Progress'])
    completed = len([t for t in assigned_tickets if t['status'] == 'Closed'])
    
    stats = {
        'total_assigned': total_assigned,
        'in_progress': in_progress,
        'completed': completed
    }
    
    return render_template('technician/dashboard.html', tickets=assigned_tickets, stats=stats)

@app.route('/technician/update_ticket/<int:ticket_id>', methods=['POST'])
@login_required
@role_required(['technician'])
def update_ticket(ticket_id):
    status = request.form.get('status')
    comment = request.form.get('comment')
    resolution_notes = request.form.get('resolution_notes')
    satisfaction_rating = request.form.get('satisfaction_rating')

    # Verify ticket is assigned to this technician
    ticket = db.get_ticket_by_id(ticket_id)
    
    if not ticket or ticket['assignedto'] != session.get('user_id'):
        flash('Ticket not found or not assigned to you', 'error')
        return redirect(url_for('technician_dashboard'))

    # Update ticket using Supabase
    update_data = {
        'status': status,
        'updatedat': datetime.now().isoformat()
    }
    
    if status in ['Resolved', 'Closed']:
        update_data['resolvedat'] = datetime.now().isoformat()
        update_data['resolvedby'] = session.get('user_id')
    
    if resolution_notes:
        update_data['resolution_notes'] = resolution_notes
    
    if satisfaction_rating:
        update_data['satisfaction_rating'] = int(satisfaction_rating)
    
    db.update_ticket(ticket_id, update_data)
    
    # Add comment if provided
    if comment:
        db.create_comment({
            'content': comment,
            'ticketid': ticket_id,
            'userid': session.get('user_id')
        })

    flash('Ticket updated successfully', 'success')
    return redirect(url_for('technician_dashboard'))

# ==================== USER (STAFF/STUDENT) ROUTES ====================

@app.route('/user/dashboard')
@login_required
@role_required(['staff', 'student'])
def user_dashboard():
    user_id = session.get('user_id')
    
    # Get user's tickets from Supabase
    tickets = db.get_tickets_by_user(user_id)
    
    return render_template('user/dashboard.html', tickets=tickets, user_role=session.get('role'))

@app.route('/user/connect_technician')
@login_required
@role_required(['staff', 'admin'])
def connect_technician():
    """Direct technician connection page for staff"""
    return render_template('user/connect_technician.html')

def auto_assign_ticket(ticket_id, category):
    """
    Automatically assign ticket to the best available technician
    Returns technician info if assigned, None otherwise
    """
    try:
        # Get all technicians
        response = db.client.table('user').select('*').eq('role', 'technician').eq('isapproved', True).execute()
        technicians = response.data
        
        # Get active tickets count for each technician
        tech_workload = {}
        for tech in technicians:
            active_tickets = db.client.table('ticket').select('*').eq('assignedto', tech['userid']).in_('status', ['Open', 'In Progress']).execute()
            tech_workload[tech['userid']] = len(active_tickets.data)
        
        # Get presence info
        response = db.client.table('user_presence').select('*').in_('userid', [tech['userid'] for tech in technicians]).execute()
        presence_map = {p['userid']: p for p in response.data}
        
        # Sort technicians by availability
        best_technician = None
        now = datetime.now()
        
        for tech in technicians:
            tech_id = tech['userid']
            presence = presence_map.get(tech_id, {})
            online_status = presence.get('status', 'offline')
            last_seen = presence.get('last_seen')
            
            # Skip if offline and has been offline for more than 1 hour
            if online_status != 'online':
                if last_seen:
                    try:
                        last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                        if (now - last_seen_dt).total_seconds() > 3600:  # 1 hour
                            continue
                    except:
                        continue
                else:
                    continue
            
            # Check if technician has capacity (max 5 active tickets)
            if tech_workload.get(tech_id, 0) < 5:
                best_technician = {
                    'userid': tech_id,
                    'name': tech['name'],
                    'email': tech['email'],
                    'active_tickets': tech_workload.get(tech_id, 0),
                    'online_status': online_status
                }
                break
        
        # Assign ticket if we found a suitable technician
        if best_technician:
            db.update_ticket(ticket_id, {
                'assignedto': best_technician['userid'],
                'status': 'In Progress',
                'updatedat': now.isoformat()
            })
            
            # Log the assignment
            print(f"Auto-assigned ticket {ticket_id} to {best_technician['name']} (workload: {best_technician['active_tickets']})")
            return best_technician
        else:
            print(f"No available technician found for ticket {ticket_id}")
            return None
            
    except Exception as e:
        print(f"❌ Auto-assign failed: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/user/create_ticket', methods=['GET', 'POST'])
@login_required
@role_required(['staff', 'student'])
def create_ticket():
    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        
        filepath = None
        if 'file' in request.files:
            file = request.files['file']
            if file and file.filename and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"{timestamp}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
        
        # Create ticket using Supabase
        new_ticket = db.create_ticket({
            'title': title,
            'description': description,
            'category': category,
            'userid': session.get('user_id'),
            'filepath': filepath,
            'status': 'Open'
        })
        
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
        else:
            flash('Failed to create ticket', 'error')
        
        return redirect(url_for('user_dashboard'))
    
    categories = ['Hardware', 'Software', 'Network', 'Printer', 'Account Access', 'Other']
    return render_template('user/create_ticket.html', categories=categories)

@app.route('/user/view_ticket/<int:ticket_id>')
@login_required
def view_ticket(ticket_id):
    try:
        # Get ticket details from Supabase
        ticket = db.get_ticket_by_id(ticket_id)
        
        if not ticket:
            flash('Ticket not found', 'error')
            return redirect(url_for('dashboard'))
        
        # Authorization check
        role = session.get('role')
        user_id = session.get('user_id')
        
        # Ensure user_id is integer
        try:
            user_id = int(user_id)
        except (ValueError, TypeError):
            flash('Invalid user ID', 'error')
            return redirect(url_for('dashboard'))
        
        # Get ticket user IDs safely
        ticket_user_id = ticket.get('userid')
        ticket_assigned_to = ticket.get('assignedto')
        
        # Convert to integers if they exist
        try:
            ticket_user_id = int(ticket_user_id) if ticket_user_id is not None else None
        except (ValueError, TypeError):
            ticket_user_id = None
            
        try:
            ticket_assigned_to = int(ticket_assigned_to) if ticket_assigned_to is not None else None
        except (ValueError, TypeError):
            ticket_assigned_to = None
        
        # Check authorization: Admin can view any ticket, others only their own or assigned tickets
        is_admin = role in ['admin']
        is_creator = ticket_user_id == user_id
        is_assignee = ticket_assigned_to == user_id
        
        if not is_admin and not is_creator and not is_assignee:
            flash('Access denied', 'error')
            return redirect(url_for('dashboard'))
        
        # NEW: Only fetch comments for staff, technicians, and admin (NOT students)
        comments = []
        can_comment = role in ['admin', 'technician', 'staff']
        
        if can_comment:
            comments = db.get_comments_by_ticket(ticket_id)
        
        # Check for active work session (for technicians only)
        active_session = None
        if role == 'technician' and ticket_assigned_to == user_id:
            try:
                tech_id = session.get('user_id')
                work_response = db.client.table('technician_work_log').select('*')\
                    .eq('technicianid', tech_id)\
                    .eq('ticketid', ticket_id)\
                    .is_('end_time', None)\
                    .order('start_time', desc=True)\
                    .limit(1)\
                    .execute()
                
                if work_response.data and len(work_response.data) > 0:
                    active_session = work_response.data[0]
                    # Convert start_time to timestamp for JavaScript
                    from datetime import datetime as dt
                    start_dt = dt.fromisoformat(active_session['start_time'].replace('Z', '+00:00'))
                    active_session['start_time_ts'] = int(start_dt.timestamp() * 1000)
            except Exception as e:
                print(f"Warning: Could not fetch active session: {e}")
        
        return render_template('view_ticket.html', 
                             ticket=ticket, 
                             comments=comments,
                             can_comment=can_comment,
                             active_session=active_session)
    except Exception as e:
        print(f"❌ Error viewing ticket {ticket_id}: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading ticket details', 'error')
        return redirect(url_for('dashboard'))

@app.route('/ticket/<int:ticket_id>/comment', methods=['POST'])
@login_required
def add_comment(ticket_id):
    # NEW: Block students from commenting
    if session.get('role') == 'student':
        flash('Students cannot add comments. If you need assistance, please contact your professor or create a new ticket with more details.', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    content = request.form.get('content')
    
    if not content:
        flash('Comment cannot be empty', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    # Verify ticket exists
    ticket = db.get_ticket_by_id(ticket_id)
    
    if not ticket:
        flash('Ticket not found', 'error')
        return redirect(url_for('dashboard'))
    
    role = session.get('role')
    user_id = session.get('user_id')
    
    # Ensure user_id is integer
    try:
        user_id = int(user_id)
    except (ValueError, TypeError):
        flash('Invalid user ID', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    
    # Get ticket user IDs safely
    ticket_user_id = ticket.get('userid')
    ticket_assigned_to = ticket.get('assignedto')
    
    # Convert to integers if they exist
    try:
        ticket_user_id = int(ticket_user_id) if ticket_user_id is not None else None
    except (ValueError, TypeError):
        ticket_user_id = None
        
    try:
        ticket_assigned_to = int(ticket_assigned_to) if ticket_assigned_to is not None else None
    except (ValueError, TypeError):
        ticket_assigned_to = None
    
    # Authorization: Admin can comment on any ticket, others only on their own or assigned tickets
    is_admin = role in ['admin']
    is_creator = ticket_user_id == user_id
    is_assignee = ticket_assigned_to == user_id
    
    if not is_admin and not is_creator and not is_assignee:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Add comment using Supabase
    try:
        db.create_comment({
            'content': content,
            'ticketid': ticket_id,
            'userid': user_id
        })
        
        flash('Comment added successfully', 'success')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))
    except Exception as e:
        print(f"❌ Error creating comment: {e}")
        import traceback
        traceback.print_exc()
        flash('Error adding comment', 'error')
        return redirect(url_for('view_ticket', ticket_id=ticket_id))

# ==================== PROFILE & SETTINGS ====================

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        current_password = request.form.get('current_password')
        new_password = request.form.get('new_password')
        
        user = db.get_user_by_id(session.get('user_id'))
        
        if check_password_hash(user['passwordhash'], current_password):
            new_hash = generate_password_hash(new_password)
            db.update_user(session.get('user_id'), {'passwordhash': new_hash})
            flash('Password updated successfully', 'success')
        else:
            flash('Current password is incorrect', 'error')
        
        return redirect(url_for('profile'))
    
    user = db.get_user_by_id(session.get('user_id'))
    
    return render_template('profile.html', user=user)

# ==================== CHATBOT ROUTES ====================




# ==================== CHATBOT ROUTES WITH ROLE VALIDATION ====================

@app.route('/api/chat/start', methods=['POST'])
@login_required
def start_chat_session():
    """Start a new chat session for all users"""
    try:
        # Check if Supabase is connected
        if not db.client:
            return jsonify({
                'success': False,
                'error': 'Database connection not available'
            }), 500
        
        # Get user_id from session and validate
        session_user_id = session.get('user_id')
        if not session_user_id:
            print(f"⚠️ No user_id in session - Session data: {dict(session)}")
            return jsonify({
                'success': False,
                'error': 'User ID not found in session'
            }), 500
        
        # Ensure user_id is an integer
        try:
            user_id = int(session_user_id)
        except (ValueError, TypeError) as e:
            print(f"❌ Invalid user_id format: {session_user_id}, type: {type(session_user_id)}, error: {e}")
            return jsonify({
                'success': False,
                'error': f'Invalid user ID format: {session_user_id}'
            }), 500
        
        print(f"🔍 Starting chat session for user_id: {user_id}")
        
        # First, verify the user exists
        user_check = db.client.table('user').select('userid, name, role').eq('userid', user_id).execute()
        if not user_check.data:
            print(f"⚠️ User {user_id} not found in database")
            return jsonify({
                'success': False,
                'error': 'User not found'
            }), 404
        
        print(f"✅ User verified: {user_check.data[0]['name']} ({user_check.data[0]['role']})")
        
        # Check for active session
        print(f"🔍 Checking for existing active chat sessions...")
        response = db.client.table('chat_session').select('*').eq('userid', user_id).eq('status', 'active').order('created_at', desc=True).limit(1).execute()
        
        print(f"📊 Query result: {len(response.data) if response.data else 0} sessions found")
        if response.data:
            print(f"📊 Raw response: {response.data[0]}")
        
        active_session = response.data[0] if response.data else None
        
        if active_session:
            session_id = active_session['sessionid']
            print(f"✅ Reusing existing chat session: {session_id} for user {user_id}")
        else:
            # Create new session - let Supabase auto-generate sessionid as integer
            print(f"🆕 Creating new chat session for user {user_id}")
            
            try:
                print(f"🔍 DEBUG: About to insert - userid={user_id} (type: {type(user_id).__name__}), status=active")
                
                # Insert with only userid and status - let DB auto-generate sessionid
                response = db.client.table('chat_session').insert({
                    'userid': user_id,  # This MUST be integer
                    'status': 'active'
                }).execute()
                
                print(f"📊 Insert response status: {response}")
                
                if response.data and len(response.data) > 0:
                    new_session = response.data[0]
                    session_id = new_session['sessionid']  # Get the auto-generated integer ID
                    print(f"✅ Created new chat session: {session_id} for user {user_id}")
                    print(f"📊 Session data: {new_session}")
                else:
                    print(f"❌ No data returned from insert")
                    return jsonify({
                        'success': False,
                        'error': 'Failed to create chat session - no data returned'
                    }), 500
                    
            except Exception as insert_error:
                print(f"❌ Insert failed: {insert_error}")
                import traceback
                print(f"Traceback: {traceback.format_exc()}")
                return jsonify({
                    'success': False,
                    'error': f'Failed to create chat session: {str(insert_error)}'
                }), 500
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': 'Chat session started'
        })
    except Exception as e:
        print(f"❌ Error starting chat session: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Failed to start chat: {str(e)}'
        }), 500

@app.route('/api/chat/message', methods=['POST'])
@login_required
def send_chat_message():
    """Handle user message and generate bot response"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        user_message = data.get('message', '').strip()
        
        # Ensure user_id is an integer
        user_id = int(session.get('user_id', 0))
        
        print(f"💬 Chat message received - Session: {session_id}, User: {user_id}")
        
        if not user_message or not session_id:
            return jsonify({'success': False, 'error': 'Invalid data'}), 400
        
        # Verify session belongs to user
        chat_session = db.get_chat_session_by_id(session_id)
        
        if not chat_session:
            print(f"❌ Chat session not found: {session_id}")
            return jsonify({'success': False, 'error': 'Session not found'}), 404
        
        if chat_session['userid'] != user_id:
            print(f"❌ Session user mismatch - Session owner: {chat_session['userid']}, Current user: {user_id}")
            return jsonify({'success': False, 'error': 'Invalid session'}), 403
        
        if chat_session['status'] != 'active':
            print(f"❌ Session not active - Status: {chat_session['status']}")
            return jsonify({'success': False, 'error': 'Session not active'}), 400
        
        # Save user message
        db.create_chat_message({
            'sessionid': session_id,
            'sender': 'user',
            'message': user_message
        })
        
        # Check if there's an active live chat with technician
        live_chat_response = db.client.table('live_chat').select('*')\
            .eq('sessionid', session_id)\
            .eq('status', 'active')\
            .execute()
        
        has_active_live_chat = live_chat_response.data and len(live_chat_response.data) > 0
        
        if has_active_live_chat:
            print(f"🔴 LIVE CHAT ACTIVE - Notifying technician (ID: {live_chat_response.data[0]['technicianid']})")
            # Don't generate bot response during live chat
            # Technician will respond directly
            return jsonify({
                'success': True,
                'bot_message': None,  # No bot message
                'message_count': 1,  # Minimal count
                'should_escalate': False,
                'live_chat_active': True
            })
        
        # Count messages in this session
        all_messages = db.get_chat_messages_by_session(session_id)
        message_count = len(all_messages)
        
        print(f"📊 Message count: {message_count}, AI Enabled: {AI_ENABLED}")
        
        # Generate bot response (only if no live chat)
        if AI_ENABLED:
            bot_response, intent = generate_ai_response(user_message, message_count, session_id)
        else:
            bot_response, intent = generate_bot_response(user_message, message_count)
        
        # Save bot response
        db.create_chat_message({
            'sessionid': session_id,
            'sender': 'bot',
            'message': bot_response,
            'intent': intent
        })
        
        # Check if should escalate (after 4+ messages or specific intents, or immediately for staff)
        user_role = session.get('role')
        should_escalate = (message_count >= 6 or 
                          intent in ['escalate', 'hardware_failure', 'account_lockout'] or
                          user_role in ['staff', 'admin'])
        
        print(f"✅ Response sent - Escalate: {should_escalate}, Intent: {intent}")
        
        return jsonify({
            'success': True,
            'bot_message': bot_response,
            'message_count': message_count,
            'should_escalate': should_escalate
        })
    except Exception as e:
        print(f"❌ Error sending chat message: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'success': False,
            'error': f'Failed to send message: {str(e)}'
        }), 500

@app.route('/api/chat/request_technician_chat', methods=['POST'])
@login_required
def request_technician_chat():
    """Request live chat with technician and notify them"""
    
    print("\n🔔 REQUEST TECHNICIAN CHAT CALLED")
    data = request.get_json()
    session_id = data.get('session_id')
    
    print(f"📝 Request data: {data}")
    print(f"Session ID: {session_id}")
    
    # Get chat session
    chat_session = db.get_chat_session_by_id(session_id)
    
    if not chat_session or chat_session['userid'] != session.get('user_id'):
        print(f"❌ Invalid session - Session: {chat_session}, User: {session.get('user_id')}")
        return jsonify({'success': False, 'error': 'Invalid session'}), 403
    
    # Get user info
    user = db.get_user_by_id(session.get('user_id'))
    print(f"👤 User: {user['name']} ({user['role']})")
    
    # Find available technician - more lenient for staff/admin
    user_role = session.get('role')
    time_window = 10 if user_role in ['staff', 'admin'] else 2  # minutes
    
    print(f"⏰ Looking for technician (time window: {time_window} min)")
    available_tech = db.get_available_technician(time_window)
    
    if available_tech:
        print(f"✅ Found available technician: {available_tech['name']} (ID: {available_tech['userid']})")
        
        print(f"🆕 Creating live chat record...")
        # Create live chat (Supabase will auto-generate livechatid as INTEGER)
        new_chat = db.create_live_chat({
            'sessionid': session_id,
            'technicianid': available_tech['userid'],
            'status': 'active'
        })
        
        print(f"📊 Live chat created: {new_chat}")
        
        # Update session status
        if db.client:
            print(f"🔄 Updating chat_session status to 'live_chat'")
            db.client.table('chat_session').update({'status': 'live_chat'}).eq('sessionid', session_id).execute()
        
        # Add system message with user info
        system_msg = f"🎯 Connected to {available_tech['name']} (Technician)\n\n📋 User Info:\n- Name: {user['name']}\n- Role: {user['role']}\n\nYou can now chat in real-time!"
        
        print(f"💬 Adding system message...")
        db.create_chat_message({
            'sessionid': session_id,
            'sender': 'bot',
            'message': system_msg,
            'intent': 'system'
        })
        
        # Add initial greeting from technician
        greeting_msg = f"Hello! I'm {available_tech['name']}, your IT technician. How can I help you today?"
        db.create_chat_message({
            'sessionid': session_id,
            'sender': 'technician',
            'message': greeting_msg,
            'intent': 'greeting'
        })
        
        print(f"✅ SUCCESS - Chat assigned to {available_tech['name']}")
        
        return jsonify({
            'success': True,
            'type': 'live_chat',
            'technician_name': available_tech['name'],
            'technician_id': available_tech['userid'],
            'live_chat_id': new_chat['livechatid'],  # Use auto-generated ID
            'message': f'✅ Connected to {available_tech["name"]}! Chat starting now...'
        })
    else:
        print(f"❌ NO TECHNICIANS AVAILABLE")
        return jsonify({
            'success': True,
            'type': 'no_availability',
            'message': '⏳ No technicians online right now.\n\nI can create a support ticket instead:\n✅ You\'ll be in the queue for the next available technician\n✅ You\'ll get email updates\n✅ Usually response within 1-2 hours\n\nWould you like me to create a ticket?'
        })




@app.route('/api/chat/request_technician', methods=['POST'])
@login_required
def request_live_technician():
    """Request live chat with available technician - ONLY for Staff and Admin"""
    
    # Block students from escalating to technician
    if session.get('role') not in ['staff', 'admin']:
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        data = request.get_json()
        session_id = data.get('session_id')
        
        # Verify session exists
        chat_session = db.get_chat_session_by_id(session_id)
        
        if not chat_session or chat_session['userid'] != session.get('user_id'):
            return jsonify({'success': False, 'error': 'Invalid session'}), 403
        
        # Find available technician (online and active within last 2 minutes)
        two_minutes_ago = datetime.now() - timedelta(minutes=2)
        
        # Get all technicians first
        response = db.client.table('user').select('*').eq('role', 'technician').eq('isapproved', True).execute()
        technicians = response.data
        
        available_tech = None
        for tech in technicians:
            # Check presence
            presence = db.client.table('user_presence').select('*').eq('userid', tech['userid']).eq('status', 'online').execute()
            if presence.data:
                last_seen = presence.data[0].get('last_seen')
                if last_seen:
                    try:
                        last_seen_dt = datetime.fromisoformat(last_seen.replace('Z', '+00:00'))
                        if last_seen_dt > two_minutes_ago:
                            # Check if not in active chat
                            active_chats = db.client.table('live_chat').select('*').eq('technicianid', tech['userid']).eq('status', 'active').execute()
                            if not active_chats.data:
                                available_tech = tech
                                break
                    except:
                        continue
        
        if available_tech:
            # Create live chat session
            new_chat = db.create_live_chat({
                'sessionid': session_id,
                'technicianid': available_tech['userid'],
                'status': 'active'
            })
            
            # Update chat session status
            db.client.table('chat_session').update({'status': 'live_chat'}).eq('sessionid', session_id).execute()
            
            # Add system message
            db.create_chat_message({
                'sessionid': session_id,
                'sender': 'bot',
                'message': f'🎯 Connected to {available_tech["name"]} (Technician). You can now chat in real-time!',
                'intent': 'system'
            })
            
            return jsonify({
                'success': True,
                'type': 'live_chat',
                'technician_name': available_tech['name'],
                'technician_id': available_tech['userid'],
                'live_chat_id': new_chat['livechatid'],
                'message': f'Connected to {available_tech["name"]}! You can now chat directly.'
            })
        else:
            return jsonify({
                'success': True,
                'type': 'no_availability',
                'message': 'No technicians are currently online. Would you like to create a support ticket instead?'
            })
    
    except Exception as e:
        print(f"❌ Error requesting technician: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to request technician: {str(e)}'}), 500

@app.route('/api/chat/escalate', methods=['POST'])
@login_required
def escalate_to_ticket():
    """Create ticket from chat session"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        data = request.get_json()
        session_id = data.get('session_id')
        category = data.get('category', 'Other')
        
        # Get chat session using Supabase
        chat_session = db.get_chat_session_by_id(session_id)
        
        if not chat_session or chat_session['userid'] != session.get('user_id'):
            return jsonify({'success': False, 'error': 'Invalid session'}), 403
        
        # Get chat messages using Supabase
        messages = db.get_chat_messages_by_session(session_id)
        
        # Build ticket description from chat history
        chat_transcript = "=== Chat Transcript ===\n\n"
        for msg in messages:
            sender = "You" if msg['sender'] == 'user' else "Bot"
            chat_transcript += f"{sender}: {msg['message']}\n\n"
        
        chat_transcript += "=== End of Chat ===\n\nThis ticket was created from an unresolved chat session."
        
        # Extract main issue from first user message
        first_user_msg = messages[0]['message'] if messages else "Issue reported via chat"
        title = first_user_msg[:100] + "..." if len(first_user_msg) > 100 else first_user_msg
        
        # Create ticket using Supabase
        new_ticket = db.create_ticket({
            'title': f"[Chat Escalation] {title}",
            'description': chat_transcript,
            'category': category,
            'userid': session.get('user_id'),
            'status': 'Open'
        })
        
        ticket_id = new_ticket['ticketid']
        
        # Update chat session using Supabase
        db.client.table('chat_session').update({
            'status': 'escalated',
            'escalated_ticket_id': ticket_id,
            'resolved_at': datetime.now().isoformat()
        }).eq('sessionid', session_id).execute()
        
        return jsonify({
            'success': True,
            'ticket_id': ticket_id,
            'message': 'Ticket created successfully. A technician will assist you soon.'
        })
    
    except Exception as e:
        print(f"❌ Error escalating to ticket: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to create ticket: {str(e)}'}), 500

@app.route('/api/chat/history/<int:session_id>')
@login_required
def get_chat_history(session_id):
    """Get chat history for a session"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        # Verify session belongs to user using Supabase
        chat_session = db.get_chat_session_by_id(session_id)
        
        if not chat_session or chat_session['userid'] != session.get('user_id'):
            return jsonify({'success': False, 'error': 'Invalid session'}), 403
        
        # Get messages using Supabase
        messages = db.get_chat_messages_by_session(session_id)
        
        return jsonify({
            'success': True,
            'messages': messages,
            'status': chat_session['status']
        })
    
    except Exception as e:
        print(f"❌ Error getting chat history: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to get chat history: {str(e)}'}), 500


# ==================== ADMIN DIRECT MESSAGING ====================

@app.route('/admin/send_direct_message', methods=['POST'])
@login_required
@role_required(['admin'])
def admin_send_direct_message():
    """Admin sends direct message to technician WITHOUT chatbot escalation"""
    
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        data = request.get_json()
        technician_id = data.get('technician_id')
        message = data.get('message', '').strip()
        ticket_id = data.get('ticket_id')  # Optional - link to ticket
        
        if not technician_id or not message:
            return jsonify({'success': False, 'error': 'Invalid request'}), 400
        
        # Verify technician exists and is approved using Supabase
        tech = db.get_user_by_id(technician_id)
        
        if not tech or tech['role'] != 'technician' or not tech.get('isapproved'):
            return jsonify({'success': False, 'error': 'Technician not found'}), 404
        
        # Create a special admin message (not through chatbot)
        # Store in chat_message table with sessionid as None or a special system session
        db.client.table('chat_message').insert({
            'sessionid': None,  # Direct message, not tied to a session
            'sender': 'admin',
            'message': f"[ADMIN] {session.get('name')}: {message}",
            'intent': 'direct_message'
        }).execute()
        
        return jsonify({
            'success': True,
            'message': f'Message sent to {tech["name"]}'
        })
    
    except Exception as e:
        print(f"❌ Error sending admin message: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to send message: {str(e)}'}), 500

@app.route('/admin/technicians')
@login_required
@role_required(['admin'])
def admin_technicians():
    """View all technicians for direct messaging"""
    
    # Get all technicians with online status using Supabase
    response = db.client.table('user').select('''
        userid, name, email,
        user_presence(status, last_seen)
    ''').eq('role', 'technician').eq('isapproved', True).execute()
    
    technicians = response.data if response.data else []
    
    # Get active live chats count for each technician
    tech_list = []
    for tech in technicians:
        # Count active chats
        chats_response = db.client.table('live_chat').select('*').eq('technicianid', tech['userid']).eq('status', 'active').execute()
        active_chats = len(chats_response.data) if chats_response.data else 0
        
        # Check if online (last seen within 2 minutes)
        presence = tech.get('user_presence', {})
        is_online = False
        if presence and presence.get('status') == 'online' and presence.get('last_seen'):
            try:
                last_seen = datetime.fromisoformat(presence['last_seen'].replace('Z', '+00:00'))
                time_diff = datetime.now() - last_seen
                if time_diff.total_seconds() <= 120:  # 2 minutes
                    is_online = True
            except:
                pass
        
        tech_list.append({
            'userid': tech['userid'],
            'name': tech['name'],
            'email': tech['email'],
            'status': 'online' if is_online else 'offline',
            'last_seen': presence.get('last_seen') if presence else None,
            'active_chats': active_chats
        })
    
    return render_template('admin/technicians.html', technicians=tech_list)

# ==================== ADMIN REPORTING SYSTEM ====================

@app.route('/admin/reports')
@login_required
@role_required(['admin'])
def admin_reports():
    """Main reports dashboard"""
    return render_template('admin/reports.html')

@app.route('/admin/reports/monthly/<int:year>/<int:month>')
@login_required
@role_required(['admin'])
def monthly_report(year, month):
    """Generate monthly report for specific month"""
    
    # Format month for queries
    month_str = f"{year:04d}-{month:02d}"
    start_date = f"{month_str}-01T00:00:00"
    
    # Get next month for end date
    if month == 12:
        end_year = year + 1
        end_month = 1
    else:
        end_year = year
        end_month = month + 1
    end_date = f"{end_year:04d}-{end_month:02d}-01T00:00:00"
    
    try:
        if not db.client:
            flash('Database connection not available', 'error')
            return redirect(url_for('admin_dashboard'))
        
        # Get all tickets for the month using Supabase
        tickets_response = db.client.table('ticket').select('*')\
            .gte('createdat', start_date)\
            .lt('createdat', end_date)\
            .execute()
        
        tickets = tickets_response.data if tickets_response.data else []
        
        # Calculate statistics in Python
        total_tickets = len(tickets)
        resolved_tickets = sum(1 for t in tickets if t.get('status') in ['Resolved', 'Closed'])
        open_tickets = sum(1 for t in tickets if t.get('status') == 'Open')
        in_progress_tickets = sum(1 for t in tickets if t.get('status') == 'In Progress')
        
        # Calculate average resolution time (for resolved tickets only)
        resolution_times = []
        for ticket in tickets:
            if ticket.get('resolvedat') and ticket.get('createdat'):
                try:
                    created = datetime.fromisoformat(ticket['createdat'].replace('Z', '+00:00'))
                    resolved = datetime.fromisoformat(ticket['resolvedat'].replace('Z', '+00:00'))
                    hours = (resolved - created).total_seconds() / 3600
                    resolution_times.append(hours)
                except:
                    pass
        
        avg_resolution_hours = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Calculate average satisfaction
        ratings = [t.get('satisfaction_rating') for t in tickets if t.get('satisfaction_rating')]
        avg_satisfaction = sum(ratings) / len(ratings) if ratings else 0
        
        # Category statistics
        category_counts = {}
        for ticket in tickets:
            cat = ticket.get('category', 'Other')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        category_stats = [{'category': cat, 'total': count} for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)]
        
        # Get all technicians
        tech_response = db.client.table('user').select('*')\
            .eq('role', 'technician')\
            .eq('isapproved', True)\
            .execute()
        
        technicians = tech_response.data if tech_response.data else []
        
        # Technician performance
        technician_performance = []
        for tech in technicians:
            tech_tickets = [t for t in tickets if t.get('assignedto') == tech['userid']]
            tech_resolved = sum(1 for t in tech_tickets if t.get('status') in ['Resolved', 'Closed'])
            tech_hours = sum(t.get('time_spent_hours', 0) or 0 for t in tech_tickets)
            
            technician_performance.append({
                'technician_name': tech['name'],
                'technician_email': tech['email'],
                'tickets_assigned': len(tech_tickets),
                'tickets_resolved': tech_resolved,
                'total_hours_worked': tech_hours
            })
        
        technician_performance.sort(key=lambda x: x['tickets_resolved'], reverse=True)
        
        # Work log hours
        work_log_response = db.client.table('technician_work_log').select('*')\
            .gte('start_time', start_date)\
            .lt('start_time', end_date)\
            .execute()
        
        work_logs = work_log_response.data if work_log_response.data else []
        
        # Group by technician
        work_by_tech = {}
        for log in work_logs:
            tech_id = log.get('technicianid')
            if tech_id not in work_by_tech:
                work_by_tech[tech_id] = {
                    'total_hours': 0,
                    'ticket_sessions': 0,
                    'chat_sessions': 0,
                    'maintenance_sessions': 0
                }
            
            hours = log.get('hours_worked', 0) or 0
            work_by_tech[tech_id]['total_hours'] += hours
            
            work_type = log.get('work_type', '')
            if work_type == 'ticket_resolution':
                work_by_tech[tech_id]['ticket_sessions'] += 1
            elif work_type == 'live_chat':
                work_by_tech[tech_id]['chat_sessions'] += 1
            elif work_type == 'maintenance':
                work_by_tech[tech_id]['maintenance_sessions'] += 1
        
        # Match with technician names
        work_hours = []
        for tech in technicians:
            if tech['userid'] in work_by_tech:
                tech_data = work_by_tech[tech['userid']]
                work_hours.append({
                    'technician_name': tech['name'],
                    'technician_email': tech['email'],
                    'total_work_hours': tech_data['total_hours'],
                    'ticket_work_sessions': tech_data['ticket_sessions'],
                    'chat_sessions': tech_data['chat_sessions'],
                    'maintenance_sessions': tech_data['maintenance_sessions']
                })
        
        work_hours.sort(key=lambda x: x['total_work_hours'], reverse=True)
        
        # Daily trend
        daily_counts = {}
        for ticket in tickets:
            try:
                date_str = ticket['createdat'][:10]  # YYYY-MM-DD
                if date_str not in daily_counts:
                    daily_counts[date_str] = {'created': 0, 'resolved': 0}
                daily_counts[date_str]['created'] += 1
                if ticket.get('status') in ['Resolved', 'Closed']:
                    daily_counts[date_str]['resolved'] += 1
            except:
                pass
        
        daily_trend = [{'date': date, 'tickets_created': data['created'], 'tickets_resolved': data['resolved']} 
                      for date, data in sorted(daily_counts.items())]
        
        return render_template('admin/monthly_report.html', 
                             year=year, 
                             month=month,
                             month_name=datetime(year, month, 1).strftime('%B'),
                             ticket_stats={
                                 'total_tickets': total_tickets,
                                 'resolved_tickets': resolved_tickets,
                                 'open_tickets': open_tickets,
                                 'in_progress_tickets': in_progress_tickets,
                                 'avg_resolution_hours': avg_resolution_hours,
                                 'avg_satisfaction': avg_satisfaction
                             },
                             category_stats=category_stats,
                             technician_stats=technician_performance,
                             work_hours=work_hours,
                             daily_trend=daily_trend)
    
    except Exception as e:
        print(f"❌ Error generating monthly report: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash('Failed to generate report', 'error')
        return redirect(url_for('admin_dashboard'))

@app.route('/admin/reports/generate/<int:year>/<int:month>')
@login_required
@role_required(['admin'])
def generate_monthly_report(year, month):
    """Generate and cache monthly report"""
    # This would be called to pre-generate reports
    # For now, just redirect to view the report
    return redirect(url_for('monthly_report', year=year, month=month))

@app.route('/admin/reports/custom')
@login_required
@role_required(['admin'])
def custom_date_report():
    """Generate custom date range report"""
    try:
        if not db.client:
            flash('Database connection not available', 'error')
            return redirect(url_for('admin_dashboard'))
        
        start_date = request.args.get('start_date', '2024-01-01')
        end_date = request.args.get('end_date', '2026-01-25')
        
        # Add one day to end_date to include the full end date
        end_date_plus_one = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%dT00:00:00')
        start_datetime = f"{start_date}T00:00:00"
        
        # Get all tickets in date range
        tickets_response = db.client.table('ticket').select('*')\
            .gte('createdat', start_datetime)\
            .lt('createdat', end_date_plus_one)\
            .execute()
        
        tickets = tickets_response.data if tickets_response.data else []
        
        # Calculate statistics in Python
        total_tickets = len(tickets)
        resolved_tickets = sum(1 for t in tickets if t.get('status') in ['Resolved', 'Closed'])
        open_tickets = sum(1 for t in tickets if t.get('status') == 'Open')
        in_progress_tickets = sum(1 for t in tickets if t.get('status') == 'In Progress')
        
        # Calculate average resolution time
        resolution_times = []
        for ticket in tickets:
            if ticket.get('resolvedat') and ticket.get('createdat'):
                try:
                    created = datetime.fromisoformat(ticket['createdat'].replace('Z', '+00:00'))
                    resolved = datetime.fromisoformat(ticket['resolvedat'].replace('Z', '+00:00'))
                    hours = (resolved - created).total_seconds() / 3600
                    resolution_times.append(hours)
                except:
                    pass
        
        avg_resolution_hours = sum(resolution_times) / len(resolution_times) if resolution_times else 0
        
        # Category statistics
        category_counts = {}
        for ticket in tickets:
            cat = ticket.get('category', 'Other')
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        category_stats = [{'category': cat, 'total': count, 'resolved': 0} 
                         for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)]
        
        # Get all technicians
        tech_response = db.client.table('user').select('*')\
            .eq('role', 'technician')\
            .eq('isapproved', True)\
            .execute()
        
        technicians = tech_response.data if tech_response.data else []
        
        # Technician performance
        technician_performance = []
        for tech in technicians:
            tech_tickets = [t for t in tickets if t.get('assignedto') == tech['userid']]
            tech_resolved = sum(1 for t in tech_tickets if t.get('status') in ['Resolved', 'Closed'])
            tech_hours = sum(t.get('time_spent_hours', 0) or 0 for t in tech_tickets)
            
            technician_performance.append({
                'technician_name': tech['name'],
                'technician_email': tech['email'],
                'tickets_assigned': len(tech_tickets),
                'tickets_resolved': tech_resolved,
                'total_hours_worked': tech_hours
            })
        
        technician_performance.sort(key=lambda x: x['tickets_resolved'], reverse=True)
        
        # Work log hours
        work_log_response = db.client.table('technician_work_log').select('*')\
            .gte('start_time', start_datetime)\
            .lt('start_time', end_date_plus_one)\
            .execute()
        
        work_logs = work_log_response.data if work_log_response.data else []
        
        # Group by technician
        work_by_tech = {}
        for log in work_logs:
            tech_id = log.get('technicianid')
            if tech_id not in work_by_tech:
                work_by_tech[tech_id] = {
                    'total_hours': 0,
                    'ticket_sessions': 0,
                    'chat_sessions': 0,
                    'maintenance_sessions': 0
                }
            
            hours = log.get('hours_worked', 0) or 0
            work_by_tech[tech_id]['total_hours'] += hours
            
            work_type = log.get('work_type', '')
            if work_type == 'ticket_resolution':
                work_by_tech[tech_id]['ticket_sessions'] += 1
            elif work_type == 'live_chat':
                work_by_tech[tech_id]['chat_sessions'] += 1
            elif work_type == 'maintenance':
                work_by_tech[tech_id]['maintenance_sessions'] += 1
        
        # Match with technician names
        work_hours = []
        for tech in technicians:
            if tech['userid'] in work_by_tech:
                tech_data = work_by_tech[tech['userid']]
                work_hours.append({
                    'technician_name': tech['name'],
                    'technician_email': tech['email'],
                    'total_work_hours': tech_data['total_hours'],
                    'ticket_work_sessions': tech_data['ticket_sessions'],
                    'chat_sessions': tech_data['chat_sessions'],
                    'maintenance_sessions': tech_data['maintenance_sessions']
                })
        
        work_hours.sort(key=lambda x: x['total_work_hours'], reverse=True)
        
        # Daily trend
        daily_counts = {}
        for ticket in tickets:
            try:
                date_str = ticket['createdat'][:10]  # YYYY-MM-DD
                if date_str not in daily_counts:
                    daily_counts[date_str] = {'created': 0, 'resolved': 0}
                daily_counts[date_str]['created'] += 1
                if ticket.get('status') in ['Resolved', 'Closed']:
                    daily_counts[date_str]['resolved'] += 1
            except:
                pass
        
        daily_trend = [{'date': date, 'tickets_created': data['created'], 'tickets_resolved': data['resolved']} 
                      for date, data in sorted(daily_counts.items())]
        
        # Format date range for display
        start_display = datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')
        end_display = datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')
        
        return render_template('admin/custom_report.html',
                             start_date=start_date,
                             end_date=end_date,
                             date_range=f"{start_display} - {end_display}",
                             ticket_stats={
                                 'total_tickets': total_tickets,
                                 'resolved_tickets': resolved_tickets,
                                 'open_tickets': open_tickets,
                                 'in_progress_tickets': in_progress_tickets,
                                 'avg_resolution_hours': avg_resolution_hours
                             },
                             category_stats=category_stats,
                             technician_stats=technician_performance,
                             work_hours=work_hours,
                             daily_trend=daily_trend,
                             datetime=datetime)
    
    except Exception as e:
        print(f"❌ Error generating custom report: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash('Failed to generate report', 'error')
        return redirect(url_for('admin_dashboard'))

# ==================== TECHNICIAN WORK LOGGING ====================

@app.route('/api/work/start', methods=['POST'])
@login_required
@role_required(['technician'])
def start_work_session():
    """Start a work session for technician"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        data = request.get_json()
        work_type = data.get('work_type', 'other')
        ticket_id = data.get('ticket_id')
        description = data.get('description', '')
        
        if work_type not in ['ticket_resolution', 'live_chat', 'maintenance', 'other']:
            return jsonify({'success': False, 'error': 'Invalid work type'}), 400
        
        tech_id = session.get('user_id')
        
        # Check if there's already an active session using Supabase
        response = db.client.table('technician_work_log').select('*')\
            .eq('technicianid', tech_id)\
            .is_('end_time', None)\
            .execute()
        
        if response.data and len(response.data) > 0:
            return jsonify({'success': False, 'error': 'Active work session already exists'}), 400
        
        # Start new work session using Supabase
        new_session = db.client.table('technician_work_log').insert({
            'technicianid': tech_id,
            'ticketid': ticket_id,
            'work_type': work_type,
            'start_time': datetime.now().isoformat(),
            'description': description
        }).execute()
        
        worklog_id = new_session.data[0]['worklogid'] if new_session.data else None
        
        return jsonify({
            'success': True,
            'worklog_id': worklog_id,
            'message': f'Work session started for {work_type}'
        })
    
    except Exception as e:
        print(f"❌ Error starting work session: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to start work session: {str(e)}'}), 500

@app.route('/api/work/end/<int:worklog_id>', methods=['POST'])
@login_required
@role_required(['technician'])
def end_work_session(worklog_id):
    """End a work session and calculate hours"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        tech_id = session.get('user_id')
        
        # Get the work session using Supabase
        response = db.client.table('technician_work_log').select('*')\
            .eq('worklogid', worklog_id)\
            .eq('technicianid', tech_id)\
            .is_('end_time', None)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({'success': False, 'error': 'Work session not found or already ended'}), 404
        
        work_session = response.data[0]
        
        # Calculate hours worked
        start_time = datetime.fromisoformat(work_session['start_time'])
        end_time = datetime.now()
        hours_worked = (end_time - start_time).total_seconds() / 3600
        
        # Update the session using Supabase
        db.client.table('technician_work_log').update({
            'end_time': end_time.isoformat(),
            'hours_worked': hours_worked
        }).eq('worklogid', worklog_id).execute()
        
        # If this was ticket resolution, update ticket time_spent_hours
        if work_session.get('ticketid') and work_session['work_type'] == 'ticket_resolution':
            # Get current ticket time
            ticket = db.get_ticket_by_id(work_session['ticketid'])
            current_hours = ticket.get('time_spent_hours', 0) or 0
            new_hours = current_hours + hours_worked
            
            db.client.table('ticket').update({
                'time_spent_hours': new_hours,
                'updatedat': datetime.now().isoformat()
            }).eq('ticketid', work_session['ticketid']).execute()
        
        # Format hours worked for display
        total_seconds = int(hours_worked * 3600)
        hrs = total_seconds // 3600
        mins = (total_seconds % 3600) // 60
        secs = total_seconds % 60
        hours_display = f"{hrs:02d}:{mins:02d}:{secs:02d}"
        
        return jsonify({
            'success': True,
            'hours_worked': round(hours_worked, 2),
            'hours_worked_display': hours_display,
            'message': f'Work session ended. {hours_display} logged.'
        })
    
    except Exception as e:
        print(f"❌ Error ending work session: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to end work session: {str(e)}'}), 500

@app.route('/api/work/active')
@login_required
@role_required(['technician'])
def get_active_work_session():
    """Get current active work session for technician"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        tech_id = session.get('user_id')
        
        # Get active session using Supabase
        response = db.client.table('technician_work_log').select('*')\
            .eq('technicianid', tech_id)\
            .is_('end_time', None)\
            .order('start_time', desc=True)\
            .limit(1)\
            .execute()
        
        if response.data and len(response.data) > 0:
            active_session = response.data[0]
            return jsonify({
                'active': True,
                'worklog_id': active_session['worklogid'],
                'work_type': active_session['work_type'],
                'start_time': active_session['start_time'],
                'description': active_session['description'],
                'ticket_id': active_session['ticketid']
            })
        else:
            return jsonify({'active': False})
    
    except Exception as e:
        print(f"❌ Error getting active work session: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to get active session: {str(e)}'}), 500

@app.route('/api/work/sessions/history')
@login_required
@role_required(['technician'])
def get_work_sessions_history():
    """Get work sessions history for current month"""
    try:
        print(f"🔍 Fetching work sessions for technician ID: {session.get('user_id')}")
        
        if not db.client:
            print("❌ Database client not available")
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        tech_id = session.get('user_id')
        
        # Get work sessions for current month
        current_month = datetime.now().strftime('%Y-%m')
        start_date = f"{current_month}-01T00:00:00"
        
        print(f"📅 Fetching sessions from {start_date} to present")
        
        response = db.client.table('technician_work_log').select('*')\
            .eq('technicianid', tech_id)\
            .gte('start_time', start_date)\
            .order('start_time', desc=True)\
            .execute()
        
        work_sessions = response.data if response.data else []
        print(f"✅ Found {len(work_sessions)} work sessions")
        
        return jsonify({'success': True, 'sessions': work_sessions})
    
    except Exception as e:
        print(f"❌ Error getting work sessions history: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to get work sessions: {str(e)}'}), 500

@app.route('/api/ticket/start_work/<int:ticket_id>', methods=['POST'])
@login_required
@role_required(['technician'])
def start_working_on_ticket(ticket_id):
    """Start working on a specific ticket - creates work log entry"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        tech_id = session.get('user_id')
        
        # Check if there's already an active session for this ticket
        existing = db.client.table('technician_work_log').select('*')\
            .eq('technicianid', tech_id)\
            .eq('ticketid', ticket_id)\
            .is_('end_time', None)\
            .execute()
        
        if existing.data and len(existing.data) > 0:
            # Return existing session
            active = existing.data[0]
            return jsonify({
                'success': True,
                'worklog_id': active['worklogid'],
                'message': 'Continuing work session',
                'already_active': True
            })
        
        # Create new work log entry
        now = datetime.now()
        response = db.client.table('technician_work_log').insert({
            'technicianid': tech_id,
            'ticketid': ticket_id,
            'work_type': 'ticket_resolution',
            'start_time': now.isoformat(),
            'description': f'Working on ticket #{ticket_id}'
        }).execute()
        
        worklog_id = response.data[0]['worklogid']
        
        return jsonify({
            'success': True,
            'worklog_id': worklog_id,
            'message': 'Work session started successfully'
        })
    
    except Exception as e:
        print(f"❌ Error starting work on ticket: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to start work: {str(e)}'}), 500

@app.route('/technician/work_log')
@login_required
@role_required(['technician'])
def technician_work_log():
    """View technician's work log"""
    tech_id = session.get('user_id')
    
    # Get work sessions for current month
    current_month = datetime.now().strftime('%Y-%m')
    start_date = f"{current_month}-01T00:00:00"
    
    # Get work sessions
    response = db.client.table('technician_work_log').select('*')\
        .eq('technicianid', tech_id)\
        .gte('start_time', start_date)\
        .order('start_time', desc=True)\
        .execute()
    
    work_sessions = response.data if response.data else []
    
    # Calculate monthly totals
    monthly_stats = {
        'total_sessions': 0,
        'total_hours': 0,
        'ticket_hours': 0,
        'chat_hours': 0,
        'maintenance_hours': 0
    }
    
    for work_session in work_sessions:
        if work_session.get('end_time') and work_session.get('hours_worked'):
            monthly_stats['total_sessions'] += 1
            total_hours = work_session.get('hours_worked', 0)
            monthly_stats['total_hours'] += total_hours
            
            work_type = work_session.get('work_type', '')
            if work_type == 'ticket_resolution':
                monthly_stats['ticket_hours'] += total_hours
            elif work_type == 'live_chat':
                monthly_stats['chat_hours'] += total_hours
            elif work_type == 'maintenance':
                monthly_stats['maintenance_hours'] += total_hours
    
    # Helper function to format time in 12-hour format
    def format_time_12hr(iso_datetime):
        if not iso_datetime:
            return '--'
        try:
            dt = datetime.fromisoformat(iso_datetime.replace('Z', '+00:00'))
            return dt.strftime('%I:%M:%S %p')  # 12-hour format with AM/PM
        except:
            return iso_datetime
    
    # Helper function to format duration from hours
    def format_duration(hours):
        if not hours:
            return '--'
        try:
            total_seconds = int(float(hours) * 3600)
            hrs = total_seconds // 3600
            mins = (total_seconds % 3600) // 60
            secs = total_seconds % 60
            return f"{hrs:02d}:{mins:02d}:{secs:02d}"
        except:
            return '--'
    
    # Make helpers available to template
    import jinja2
    @jinja2.pass_context
    def format_time_12hr_ctx(ctx, iso_datetime):
        return format_time_12hr(iso_datetime)
    
    @jinja2.pass_context
    def format_duration_ctx(ctx, hours):
        return format_duration(hours)
    
    # Add to template globals
    app.jinja_env.globals.update(format_time_12hr=format_time_12hr)
    app.jinja_env.globals.update(format_duration=format_duration)
    
    return render_template('technician/work_log.html', 
                         work_sessions=work_sessions,
                         monthly_stats=monthly_stats,
                         current_month=current_month)

# ==================== PRESENCE TRACKING ====================

@app.route('/api/presence/update', methods=['POST'])
@login_required
def update_presence():
    """Update user online status"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        user_id = session.get('user_id')
        
        # Check if presence record exists
        existing = db.client.table('user_presence').select('*').eq('userid', user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update existing record
            db.client.table('user_presence').update({
                'status': 'online',
                'last_seen': datetime.now().isoformat()
            }).eq('userid', user_id).execute()
        else:
            # Insert new record
            db.client.table('user_presence').insert({
                'userid': user_id,
                'status': 'online',
                'last_seen': datetime.now().isoformat()
            }).execute()
        
        return jsonify({'success': True})
    
    except Exception as e:
        print(f"❌ Error updating presence: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to update presence: {str(e)}'}), 500

@app.route('/api/presence/technicians')
@login_required
def get_online_technicians():
    """Get list of online technicians"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        # Get all approved technicians using Supabase
        response = db.client.table('user').select('*')\
            .eq('role', 'technician')\
            .eq('isapproved', True)\
            .execute()
        
        technicians = response.data if response.data else []
        
        # Filter for online ones (last seen within 2 minutes)
        two_minutes_ago = datetime.now() - timedelta(minutes=2)
        online_techs = []
        
        for tech in technicians:
            # Check presence
            presence_response = db.client.table('user_presence').select('*')\
                .eq('userid', tech['userid'])\
                .eq('status', 'online')\
                .execute()
            
            if presence_response.data:
                presence = presence_response.data[0]
                last_seen_str = presence.get('last_seen')
                if last_seen_str:
                    try:
                        last_seen = datetime.fromisoformat(last_seen_str.replace('Z', '+00:00'))
                        if last_seen > two_minutes_ago:
                            online_techs.append({
                                'userid': tech['userid'],
                                'name': tech['name'],
                                'email': tech['email'],
                                'status': 'online',
                                'last_seen': last_seen_str
                            })
                    except:
                        continue
        
        return jsonify({
            'success': True,
            'technicians': online_techs,
            'count': len(online_techs)
        })
    
    except Exception as e:
        print(f"❌ Error getting online technicians: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to get technicians: {str(e)}'}), 500

# ==================== LIVE CHAT HANDOFF ====================

@app.route('/api/chat/end_live_chat/<int:live_chat_id>', methods=['POST'])
@login_required
def end_live_chat(live_chat_id):
    """End live chat session (technician version)"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        # Get live chat details
        response = db.client.table('live_chat').select('*').eq('livechatid', live_chat_id).execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({'success': False, 'error': 'Live chat not found'}), 404
        
        live_chat = response.data[0]
        
        # Update live_chat status to ended
        db.client.table('live_chat').update({
            'status': 'ended',
            'ended_at': datetime.now().isoformat()
        }).eq('livechatid', live_chat_id).execute()
        
        # Update chat_session status to resolved
        db.client.table('chat_session').update({
            'status': 'resolved',
            'resolved_at': datetime.now().isoformat()
        }).eq('sessionid', live_chat['sessionid']).execute()
        
        # Insert system message
        db.client.table('chat_message').insert({
            'sessionid': live_chat['sessionid'],
            'sender': 'bot',
            'message': '✅ Chat session ended. Thank you for using UniHelp!',
            'intent': 'system'
        }).execute()
        
        return jsonify({'success': True, 'message': 'Live chat ended'})
    
    except Exception as e:
        print(f"❌ Error ending live chat: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to end live chat: {str(e)}'}), 500

@app.route('/api/chat/end_session', methods=['POST'])
@login_required
def end_chat_session():
    """End chat session (user version - ends by session_id)"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'Session ID required'}), 400
        
        # Verify user owns this session
        chat_session = db.get_chat_session_by_id(session_id)
        if not chat_session or chat_session['userid'] != session.get('user_id'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Check if there's an active live chat
        live_chat_response = db.client.table('live_chat').select('*')\
            .eq('sessionid', session_id)\
            .eq('status', 'active')\
            .execute()
        
        if live_chat_response.data and len(live_chat_response.data) > 0:
            live_chat = live_chat_response.data[0]
            
            # Update live_chat status to ended
            db.client.table('live_chat').update({
                'status': 'ended',
                'ended_at': datetime.now().isoformat()
            }).eq('livechatid', live_chat['livechatid']).execute()
        
        # Update chat_session status to resolved
        db.client.table('chat_session').update({
            'status': 'resolved',
            'resolved_at': datetime.now().isoformat()
        }).eq('sessionid', session_id).execute()
        
        # Insert system message
        db.client.table('chat_message').insert({
            'sessionid': session_id,
            'sender': 'bot',
            'message': '✅ Live chat session ended by user. Thank you for using UniHelp!',
            'intent': 'system'
        }).execute()
        
        return jsonify({'success': True, 'message': 'Chat session ended successfully'})
    
    except Exception as e:
        print(f"❌ Error ending chat session: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to end chat session: {str(e)}'}), 500

@app.route('/technician/live_chats')
@login_required
@role_required(['technician'])
def technician_live_chats():
    """View active live chat sessions"""
    tech_id = session.get('user_id')
    
    # Get active live chats for this technician
    response = db.client.table('live_chat').select('*')\
        .eq('technicianid', tech_id)\
        .eq('status', 'active')\
        .execute()
    
    live_chats = []
    if response.data:
        for chat in response.data:
            # Get user info from chat_session separately
            session_response = db.client.table('chat_session').select('userid').eq('sessionid', chat['sessionid']).execute()
            
            user_info = {}
            if session_response.data and len(session_response.data) > 0:
                user_id = session_response.data[0]['userid']
                user_response = db.client.table('user').select('name, email, role').eq('userid', user_id).execute()
                if user_response.data and len(user_response.data) > 0:
                    user_info = user_response.data[0]
            
            live_chats.append({
                'livechatid': chat['livechatid'],
                'sessionid': chat['sessionid'],
                'technicianid': chat['technicianid'],
                'status': chat['status'],
                'started_at': chat['started_at'],
                'ended_at': chat.get('ended_at'),
                'user_name': user_info.get('name', 'Unknown') if user_info else 'Unknown',
                'user_email': user_info.get('email', '') if user_info else '',
                'user_role': user_info.get('role', '') if user_info else ''
            })
    
    return render_template('technician/live_chats.html', live_chats=live_chats)

@app.route('/api/chat/technician/send', methods=['POST'])
@login_required
@role_required(['technician'])
def technician_send_message():
    """Technician sends message in live chat"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        data = request.get_json()
        session_id = data.get('session_id')
        message = data.get('message', '').strip()
        
        if not message:
            return jsonify({'success': False, 'error': 'Empty message'}), 400
        
        tech_id = session.get('user_id')
        
        # Verify technician is assigned to this live chat
        response = db.client.table('live_chat').select('*')\
            .eq('sessionid', session_id)\
            .eq('technicianid', tech_id)\
            .eq('status', 'active')\
            .execute()
        
        if not response.data or len(response.data) == 0:
            return jsonify({'success': False, 'error': 'Not authorized or chat not active'}), 403
        
        # Insert message
        db.client.table('chat_message').insert({
            'sessionid': session_id,
            'sender': 'technician',
            'message': message
        }).execute()
        
        return jsonify({'success': True, 'message': 'Message sent'})
    
    except Exception as e:
        print(f"❌ Error sending technician message: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to send message: {str(e)}'}), 500

@app.route('/api/chat/session/<session_id>/messages', methods=['GET'])
@login_required
def get_session_messages(session_id):
    """Get technician messages for a chat session (for polling)"""
    try:
        if not db.client:
            return jsonify({'success': False, 'error': 'Database connection not available'}), 500
        
        # Get only technician messages from this session
        response = db.client.table('chat_message').select('*')\
            .eq('sessionid', session_id)\
            .eq('sender', 'technician')\
            .order('created_at', desc=False)\
            .execute()
        
        messages = response.data if response.data else []
        
        return jsonify({'success': True, 'messages': messages})
    
    except Exception as e:
        print(f"❌ Error fetching session messages: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'success': False, 'error': f'Failed to fetch messages: {str(e)}'}), 500

def generate_bot_response(user_message, message_count):
    """
    Enhanced NLP bot response with fuzzy matching and context awareness
    Returns: (response_text, intent)
    """
    user_message_lower = user_message.lower()
    
    # Enhanced FAQ Knowledge Base with natural variations
    faq_responses = {
        'password': {
            'keywords': [
                'password', 'reset password', 'forgot password', 'change password', 
                'login issue', 'cant login', "can't login", 'cannot login',
                'locked out', 'account locked', 'reset my password',
                'forgotten password', 'password not working', 'wrong password',
                'credential', 'sign in problem', 'authentication'
            ],
            'patterns': [
                r'\b(forgot|reset|change|lost|recover)\s+(my\s+)?(password|pass|pw)\b',
                r'\bcant?\s+(log|sign)\s+in\b',
                r'\b(password|login)\s+(not|isnt|doesn\'?t)\s+work(ing)?\b',
                r'\blocked\s+out\b'
            ],
            'response': '''Hey there! 🔑 I totally get how frustrating it can be when you can't access your account.

**Let's get your password reset sorted:**

First, try the self-service option:
• Go to the login page and click "Forgot Password"
• Enter your email address
• Check your inbox (and spam folder) for the reset link
• Follow the instructions to create a new password

If that doesn't work or you don't receive the email:
• Contact your IT administrator directly
• Visit the IT help desk in person if you're on campus
• I can create a priority support ticket to get this escalated

**Quick tip:** Most password issues resolve within 30 minutes of the reset request. Try waiting a bit if you just requested it.

Would you like me to create a support ticket for immediate assistance?'''
        },
        'printer': {
            'keywords': [
                'printer', 'print', 'printing', 'scanner', 'scan', 'scanning',
                'paper jam', 'printer error', 'cant print', "can't print",
                'printer not working', 'printer offline', 'print queue',
                'toner', 'ink', 'cartridge', 'print job', 'printing issue'
            ],
            'patterns': [
                r'\b(printer|print(ing)?)\s+(not|isnt|wont|doesnt|cant)\s+work(ing)?\b',
                r'\bcant?\s+print\b',
                r'\bpaper\s+jam\b',
                r'\b(printer|print(er)?)\s+(offline|error|problem|issue)\b'
            ],
            'response': '''Hey! 🖨️ Printer issues can be really annoying, especially when you need to print something important.

**Let's troubleshoot this together:**

**First, let's try the basics:**
• Make sure the printer is powered on and connected
• Check that paper is loaded properly (not jammed or empty)
• Clear any paper jams you can see
• Verify ink/toner cartridges aren't empty
• Restart both your computer and the printer

**If it's still not working:**
• **Not printing at all?** Check your print queue - there might be a stuck job
• **Poor print quality?** The printer might need cleaning or new cartridges
• **Can't find the printer?** It might be a network issue - try reconnecting

**Need hands-on help?**
Printer problems often need someone to physically check the hardware. I can connect you with a technician who can:
• Inspect the printer in person
• Update printer drivers
• Replace faulty parts if needed

What exactly is happening with your printer? Is it not responding, showing an error, or something else?'''
        },
        'network': {
            'keywords': [
                'wifi', 'wi-fi', 'internet', 'network', 'connection', 'connectivity',
                'not connecting', 'slow internet', 'no wifi', 'no internet',
                'cant connect', "can't connect", 'disconnected', 'disconnecting',
                'network error', 'connection failed', 'unable to connect',
                'ethernet', 'lan', 'vpn', 'slow network', 'buffering'
            ],
            'patterns': [
                r'\b(wifi|internet|network)\s+(not|isnt|wont|doesnt)\s+work(ing)?\b',
                r'\bcant?\s+connect\b',
                r'\bno\s+(wifi|internet|connection)\b',
                r'\b(slow|weak)\s+(internet|wifi|connection)\b',
                r'\b(keep(s)?|getting)\s+disconnect(ed|ing)\b'
            ],
            'response': '''🌐 **Network Troubleshooting**

Let's fix your connectivity issue:

**WiFi Problems:**
1. Toggle WiFi off and on
2. Forget network and reconnect
3. Restart your device
4. Move closer to access point
5. Check if others have same issue

**Slow Internet:**
• Test speed at speedtest.net
• Disconnect unused devices
• Try wired connection (Ethernet)
• Clear browser cache
• Close bandwidth-heavy apps

**Can't Connect:**
• Verify correct network name (SSID)
• Check password is correct
• Ensure WiFi is enabled on device
• Update network drivers

**VPN Issues:**
• Disconnect and reconnect VPN
• Check VPN credentials
• Try different VPN server

**Still not working?**
This might be a network infrastructure issue. I can create a ticket for our network team to investigate.

Shall I escalate this to a network technician?'''
        },
        'software': {
            'keywords': [
                'software', 'application', 'app', 'program', 'install', 'installation',
                'update', 'upgrade', 'microsoft', 'office', 'excel', 'word', 'outlook',
                'teams', 'zoom', 'adobe', 'chrome', 'browser', 'antivirus',
                'software not working', 'app crashed', 'wont open', "won't open",
                'license', 'activation', 'subscription', 'cant install'
            ],
            'patterns': [
                r'\b(install|installing|setup)\s+(software|app|program)\b',
                r'\b(software|app|program)\s+(not|wont|cant|doesnt)\s+(work|open|start)\b',
                r'\b(license|activation)\s+(error|problem|expired)\b',
                r'\bcant?\s+install\b'
            ],
            'response': '''💻 **Software Support**

I can help with software issues:

**Installation Problems:**
1. Check you have admin rights
2. Verify system requirements
3. Disable antivirus temporarily
4. Restart computer and try again
5. Download latest version

**Software Not Working:**
• Close and restart the application
• Check for updates
• Repair installation (Control Panel → Programs)
• Uninstall and reinstall
• Check for conflicting software

**License/Activation Issues:**
• Verify license key is correct
• Check subscription is active
• Connect to campus network (for network licenses)
• Sign out and sign back in

**Common Software:**
• **Microsoft Office:** Office 365 issues
• **Browsers:** Chrome, Edge, Firefox problems
• **Communication:** Teams, Zoom, Outlook
• **Adobe:** Creative Cloud apps

**Need specific software?**
Tell me which application you need help with, or I can create a ticket for software installation/licensing support.

Would you like specialized assistance?'''
        },
        'hardware': {
            'keywords': [
                'computer', 'laptop', 'desktop', 'pc', 'mouse', 'keyboard', 
                'monitor', 'screen', 'display', 'webcam', 'camera', 'microphone',
                'headset', 'speaker', 'usb', 'port', 'charger', 'battery',
                'not turning on', 'wont start', 'broken', 'damaged', 'cracked',
                'overheating', 'loud fan', 'blue screen', 'black screen',
                'freezing', 'slow performance'
            ],
            'patterns': [
                r'\b(computer|laptop|pc)\s+(wont|cant|doesnt)\s+(turn on|start|boot)\b',
                r'\b(broken|damaged|cracked)\s+(screen|keyboard|mouse)\b',
                r'\b(blue|black)\s+screen\b',
                r'\b(freezing|frozen|hang(ing)?|stuck)\b'
            ],
            'response': '''🖥️ **Hardware Troubleshooting**

Let me help diagnose your hardware issue:

**Device Won't Turn On:**
1. Check power cable firmly connected
2. Try different power outlet
3. For laptops: Check battery charge
4. Look for LED indicators
5. Hold power button for 10 seconds

**Peripheral Issues:**
• **Keyboard/Mouse:** Try different USB port or restart computer
• **Monitor:** Check cable connections and input source
• **Webcam:** Update drivers, check privacy settings
• **Audio:** Test different audio device, check volume settings

**Performance Issues:**
• **Slow Computer:** Check disk space, run antivirus scan
• **Overheating:** Clean vents, ensure proper ventilation
• **Freezing:** Close unnecessary programs, check for updates

**Physical Damage:**
• Cracked screen
• Broken keyboard keys
• Damaged ports
• Liquid spill

**⚠️ Hardware issues often require physical inspection.**

For hardware problems, I strongly recommend creating a support ticket so a technician can:
- Physically examine the device
- Run diagnostic tests
- Arrange repairs or replacements
- Loan temporary equipment if needed

Shall I create a hardware support ticket?'''
        },
        'email': {
            'keywords': [
                'email', 'outlook', 'mail', 'inbox', 'cant send email',
                "can't receive email", 'email not working', 'outlook error',
                'mailbox full', 'email attachment', 'spam', 'junk mail'
            ],
            'patterns': [
                r'\b(email|mail|outlook)\s+(not|wont|cant|doesnt)\s+work(ing)?\b',
                r'\bcant?\s+(send|receive)\s+(email|mail)\b',
                r'\b(mailbox|inbox)\s+full\b'
            ],
            'response': '''📧 **Email Support**

Let me help with your email issue:

**Can't Send/Receive:**
1. Check internet connection
2. Verify email settings (SMTP/IMAP/POP)
3. Check mailbox storage quota
4. Review blocked senders list
5. Clear Outlook cache

**Outlook Issues:**
• Restart Outlook
• Run Outlook in Safe Mode
• Create new Outlook profile
• Repair Office installation

**Attachment Problems:**
• Check file size limit (usually 25MB)
• Try compressing large files
• Use cloud storage links instead

**Spam/Junk Mail:**
• Mark as spam/junk
• Create rules to filter
• Check junk folder for legitimate emails

Would you like me to create a ticket for email configuration assistance?'''
        },
        'account': {
            'keywords': [
                'account', 'username', 'user id', 'account locked', 'access denied',
                'permissions', 'cant access', "can't access", 'need access',
                'shared folder', 'drive access', 'directory access'
            ],
            'patterns': [
                r'\baccount\s+(locked|suspended|disabled)\b',
                r'\bneed\s+access\s+to\b',
                r'\bcant?\s+access\b',
                r'\baccess\s+denied\b'
            ],
            'response': '''👤 **Account Access Support**

I can help with account issues:

**Account Locked:**
• Wait 30 minutes for auto-unlock
• Reset password may unlock account
• Contact administrator for manual unlock

**Access Permissions:**
• Verify you have required role/permissions
• Check with resource owner for access
• May need manager approval

**Shared Resources:**
• Network drives
• Shared folders
• Database access
• Application permissions

I can create a ticket for account management team to:
- Unlock your account
- Grant required permissions
- Reset credentials
- Modify access levels

Would you like me to create an access request ticket?'''
        },
        'greeting': {
            'keywords': [
                'hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening',
                'greetings', 'howdy', 'yo', 'sup', 'help', 'start', 'begin'
            ],
            'patterns': [
                r'^(hello|hi|hey|greetings|good\s+(morning|afternoon|evening))\b',
                r'\bhelp\s+me\b'
            ],
            'response': '''Hey there! 👋 Welcome to UniHelp - your friendly IT support assistant!

I'm here to help you sort out any tech issues you might be having. Whether it's a forgotten password, printer problems, or something else entirely, I've got your back.

**Here's what I can help with:**
• 🔑 Password resets and login issues
• 🖨️ Printer and printing problems
• 🌐 WiFi and network connectivity
• 💻 Software installation and updates
• 🖥️ Hardware troubleshooting
• 📧 Email configuration issues
• 👤 Account access and permissions

**How this works:**
1. Just tell me what's going wrong in your own words
2. I'll give you step-by-step solutions to try
3. If we can't fix it together, I'll connect you with a human technician

No need for fancy technical jargon - just describe your problem naturally. What's the tech issue you're dealing with today?'''
        },
        'thanks': {
            'keywords': [
                'thank', 'thanks', 'thank you', 'appreciate', 'helpful',
                'solved', 'fixed', 'working now', 'thx', 'ty'
            ],
            'patterns': [
                r'\b(thank(s| you)?|thx|ty)\b',
                r'\b(solved|fixed|working|resolved)\b'
            ],
            'response': '''😊 **You're very welcome!**

I'm glad I could help! 

**Before you go:**
• Was this solution helpful?
• Do you have any other IT issues?
• Need help with anything else?

**Quick Tips:**
• Restart solves 80% of issues
• Keep software updated
• Back up important files regularly
• Report security concerns immediately

Feel free to chat with me anytime you need IT support. Have a great day! 🎉'''
        }
    }
    
    # Enhanced intent detection with scoring
    intent_scores = {}
    
    for intent, data in faq_responses.items():
        score = 0
        
        # Keyword matching with fuzzy logic
        for keyword in data['keywords']:
            if keyword in user_message_lower:
                score += 2
            else:
                # Fuzzy match for typos
                similarity = SequenceMatcher(None, keyword, user_message_lower).ratio()
                if similarity > 0.8:
                    score += 1
        
        # Pattern matching (regex)
        if 'patterns' in data:
            for pattern in data['patterns']:
                if re.search(pattern, user_message_lower):
                    score += 5
        
        if score > 0:
            intent_scores[intent] = score
    
    # Return highest scoring intent
    if intent_scores:
        best_intent = max(intent_scores, key=intent_scores.get)
        return (faq_responses[best_intent]['response'], best_intent)
    
    # Unknown intent - progressive escalation
    if message_count >= 4:
        return ('''🤔 **Let's Get You Expert Help**

I apologize, but I'm having trouble understanding your specific issue.

**Let me connect you with a human technician** who can better assist you.

**Benefits of creating a ticket:**
✓ Detailed documentation of your issue
✓ Direct communication with IT staff
✓ Assigned technician for your case
✓ Email updates on progress
✓ Priority handling

**Please select the category** that best matches your issue:
• Hardware (physical equipment)
• Software (applications, programs)
• Network (WiFi, internet)
• Printer/Scanner
• Account Access
• Other

Click "Create Ticket" below to get started!''', 'escalate')
    elif message_count >= 2:
        return ('''🔍 **I need more details to help you better**

Could you please provide:
• **What exactly is the problem?** (Be specific)
• **When did it start?** (Today, yesterday, ongoing?)
• **What device/software?** (Windows/Mac, specific app)
• **Any error messages?** (Exact text if possible)
• **What have you tried?** (Restart, reinstall, etc.)

**Example:** "My laptop won't connect to campus WiFi. Started this morning. No error message. I tried turning WiFi off and on."

The more details you give, the better I can assist! 😊''', 'unknown')
    else:
        return ('''👋 **I'm here to help with IT issues!**

**Common issues I handle:**
📧 **Password & Login** - Reset password, account locked
🖨️ **Printers** - Can't print, paper jams, offline
🌐 **Network** - WiFi problems, slow internet
💻 **Software** - Installation, updates, errors
🖥️ **Hardware** - Won't turn on, broken peripherals
📬 **Email** - Outlook issues, can't send/receive

**Just describe your problem naturally:**
Instead of keywords, tell me what's wrong:
• "My computer won't start"
• "I can't print from my laptop"
• "The WiFi keeps disconnecting"

What's your IT issue today? I'm listening! 🎯''', 'unknown')

def get_conversation_context(session_id):
    """Get previous conversation messages for context"""
    try:
        if not db.client:
            return []
        
        # Get messages using Supabase
        response = db.client.table('chat_message').select('*')\
            .eq('sessionid', session_id)\
            .order('created_at', desc=False)\
            .limit(15)\
            .execute()
        
        messages = response.data if response.data else []
        
        context = []
        for msg in messages:
            role = "user" if msg['sender'] == 'user' else "assistant"
            context.append({
                "role": role,
                "content": msg['message']
            })
        return context
    
    except Exception as e:
        print(f"❌ Error getting conversation context: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        return []


def generate_ai_response(user_message, message_count, session_id):
    """Enhanced Gemini AI with better IT support & faster responses"""
    if not AI_ENABLED:
        return generate_bot_response(user_message, message_count)
    
    try:
        # Get conversation context (more messages for better understanding)
        context = get_conversation_context(session_id)
        
        # Get user role for personalized responses (handle missing session gracefully)
        try:
            user_role = session.get('role', 'student')
            user_name = session.get('name', 'there')
        except RuntimeError:
            # No session context (testing or direct call)
            user_role = 'student'
            user_name = 'there'
        
        # Enhanced system prompt with comprehensive IT knowledge
        system_prompt = f"""You are an expert IT support specialist at a university helpdesk. Provide FAST, ACCURATE, and PROFESSIONAL technical support.

USER: {user_name} ({user_role}) | Conversation turn: {message_count}

YOUR EXPERTISE:
- University IT systems, policies, and common issues
- Hardware: computers, laptops, printers, scanners, peripherals
- Software: Office 365, antivirus, installation, configuration, errors
- Network: WiFi connectivity, VPN, internet access, ethernet
- Accounts: password resets, login issues, account lockouts
- Email: Outlook, Gmail, configuration, attachments, spam
- Learning Management Systems: Canvas, Blackboard, Moodle
- Security: malware, phishing, data protection

RESPONSE FRAMEWORK (CRITICAL FOR QUALITY):

1. ACKNOWLEDGE & EMPATHIZE (1 sentence)
   - "I understand that's frustrating..."
   - "Let me help you with that..."

2. DIAGNOSE QUICKLY (identify likely cause)
   - "This usually happens when..."
   - "The most common cause is..."

3. STEP-BY-STEP SOLUTION (numbered, clear actions)
   - Use numbered lists
   - One action per step
   - Be specific: "Click Start > Settings > Network"
   - Include what they should see after each step

4. VERIFY & TEST
   - "After completing these steps, try..."
   - "You should now see..."

5. ESCALATION PATH
   - If issue persists after 2-3 attempts
   - For complex hardware failures
   - Say: "Let me connect you with a technician for hands-on support"

RESPONSE QUALITY RULES:
✅ Be concise but thorough (150-400 words ideal)
✅ Use formatting: bold key terms, numbered steps
✅ Stay on topic - answer the SPECIFIC question asked
✅ Avoid generic advice - be specific to their issue
✅ Don't repeat information already provided
✅ If unsure, ask clarifying questions

ESCALATION TRIGGERS:
- Hardware failure requiring physical repair
- Issue needs admin/specialist access
- User has tried 3+ solutions without success
- Complex network/server infrastructure issue
- Security breach or data loss scenario

TONE: Professional, friendly, confident, efficient

Remember: Users want QUICK solutions, not lengthy explanations. Get to the point!"""
        
        # Build conversation
        messages = [{"role": "user", "parts": [system_prompt]}]
        
        # Add recent context (last 6 messages for efficiency)
        for msg in context[-6:]:
            messages.append({
                "role": msg["role"], 
                "parts": [msg["content"]]
            })
        
        # Add current message
        messages.append({"role": "user", "parts": [user_message]})

        print(f"🤖 AI Debug: User={user_name}, Role={user_role}, Messages={message_count}")
        print(f"🤖 Context: {len(context)} messages, Using last {min(6, len(context))}")
        
        # Generate response with optimized settings for speed & quality
        response = model.generate_content(
            messages,
            generation_config=types.GenerationConfig(
                max_output_tokens=400,  # Faster, focused responses
                temperature=0.5,  # More consistent, less random variations
                top_p=0.85,  # Better coherence
                top_k=40,  # More focused word selection
            )
        )
        
        ai_response = response.text.strip()
        print(f"🤖 AI Response: {len(ai_response)} chars - Preview: {ai_response[:100]}...")
        
        return ai_response, "ai_response"
        
    except Exception as e:
        print(f"AI Error: {e}")
        return generate_bot_response(user_message, message_count)

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

@app.route('/api/chat/status')
@login_required
def chat_status():
    """Check if AI is available"""
    ai_status = "enabled" if AI_ENABLED else "disabled"
    mode_desc = "AI-Powered (Gemini)" if AI_ENABLED else "Smart Pattern Matching (AI Disabled)"

    return jsonify({
        'ai_enabled': AI_ENABLED,
        'status': ai_status,
        'mode': mode_desc,
        'note': "AI responses are more conversational and personalized" if AI_ENABLED else "Using intelligent pattern matching - responses are still helpful!"
    })

# ==================== TECHNICIAN CHAT MANAGEMENT ====================

@app.route('/technician/new_chats', methods=['GET'])
@login_required
@role_required(['technician'])
def get_new_chats():
    """Get new chat requests for technician - API endpoint for real-time updates"""
    tech_id = session.get('user_id')
    
    print(f"🔍 Checking chats for technician ID: {tech_id}")
    
    # Get active live chats for this technician
    response = db.client.table('live_chat').select('*')\
        .eq('technicianid', tech_id)\
        .eq('status', 'active')\
        .execute()
    
    print(f"📊 Found {len(response.data) if response.data else 0} active chats")
    
    new_chats = []
    if response.data:
        for chat in response.data:
            print(f"💬 Chat found: {chat}")
            # Get session and user info
            session_response = db.client.table('chat_session').select('userid, created_at').eq('sessionid', chat['sessionid']).execute()
            
            chat_info = {
                'livechatid': chat['livechatid'],
                'sessionid': chat['sessionid'],
                'started_at': chat.get('started_at'),
                'name': 'Unknown',
                'role': 'Unknown',
                'last_message': '',
                'message_count': 0
            }
            
            if session_response.data and len(session_response.data) > 0:
                session_data = session_response.data[0]
                chat_info['created_at'] = session_data.get('created_at')
                
                # Get user info
                user_response = db.client.table('user').select('name, role').eq('userid', session_data['userid']).execute()
                if user_response.data and len(user_response.data) > 0:
                    user_data = user_response.data[0]
                    chat_info['name'] = user_data['name']
                    chat_info['role'] = user_data['role']
                
                # Get last message
                msg_response = db.client.table('chat_message').select('message').eq('sessionid', chat['sessionid']).order('created_at', desc=True).limit(1).execute()
                if msg_response.data and len(msg_response.data) > 0:
                    chat_info['last_message'] = msg_response.data[0]['message']
                
                # Get total message count
                all_msgs_response = db.client.table('chat_message').select('*', count='exact').eq('sessionid', chat['sessionid']).execute()
                chat_info['message_count'] = all_msgs_response.count if hasattr(all_msgs_response, 'count') else 0
            
            new_chats.append(chat_info)
    
    result = {
        'success': True,
        'new_chats': new_chats,
        'count': len(new_chats),
        'has_new_chat': len(new_chats) > 0,
        'debug': {
            'technician_id': tech_id,
            'total_found': len(response.data) if response.data else 0
        }
    }
    
    print(f"✅ Returning: {result}")
    return jsonify(result)


@app.route('/technician/chat/<int:live_chat_id>', methods=['GET'])
@login_required
@role_required(['technician'])
def view_technician_chat(live_chat_id):
    """View specific chat as technician"""
    try:
        if not db.client:
            flash('Database connection not available', 'error')
            return redirect(url_for('technician_dashboard'))
        
        tech_id = session.get('user_id')
        
        # Get live chat details using Supabase
        response = db.client.table('live_chat').select('*')\
            .eq('livechatid', live_chat_id)\
            .eq('technicianid', tech_id)\
            .execute()
        
        if not response.data or len(response.data) == 0:
            flash('Live chat not found', 'error')
            return redirect(url_for('technician_dashboard'))
        
        live_chat = response.data[0]
        
        # Get session and user info using Supabase
        session_response = db.client.table('chat_session').select('userid')\
            .eq('sessionid', live_chat['sessionid'])\
            .execute()
        
        user_name = 'Unknown'
        user_email = ''
        
        if session_response.data and len(session_response.data) > 0:
            user_id = session_response.data[0]['userid']
            
            # Get user details
            user_response = db.client.table('user').select('name, email')\
                .eq('userid', user_id)\
                .execute()
            
            if user_response.data and len(user_response.data) > 0:
                user_data = user_response.data[0]
                user_name = user_data['name']
                user_email = user_data['email']
        
        # Get chat messages using Supabase
        msg_response = db.client.table('chat_message').select('*')\
            .eq('sessionid', live_chat['sessionid'])\
            .order('created_at', desc=False)\
            .execute()
        
        messages = msg_response.data if msg_response.data else []
        
        return render_template('technician/chat_view.html', 
                             live_chat=live_chat,
                             messages=messages,
                             user_name=user_name,
                             user_email=user_email)
    
    except Exception as e:
        print(f"❌ Error viewing technician chat: {e}")
        import traceback
        print(f"Traceback: {traceback.format_exc()}")
        flash('Failed to load chat', 'error')
        return redirect(url_for('technician_dashboard'))

@app.route('/chatbot')
@app.route('/ai-chat')
@login_required
def chatbot():  # ← Changed from ai_chatbot to chatbot
    return render_template('ai-bot.html')

@app.route('/api/test_ai')
@login_required
def test_ai():
    """Test endpoint to check AI functionality"""
    if not AI_ENABLED:
        return jsonify({
            'status': 'AI Disabled - Using Smart Pattern Matching',
            'response': 'The chatbot uses intelligent pattern matching that provides detailed, helpful responses. To enable AI, set the GEMINI_API_KEY environment variable.',
            'setup_guide': 'See AI_SETUP.md for instructions',
            'fallback_quality': 'High - Responses are comprehensive and conversational'
        })
    
    try:
        test_message = "My computer won't start"
        response, response_type = generate_ai_response(test_message, 1, "test_session")
        
        return jsonify({
            'status': 'AI Working',
            'response_type': response_type,
            'response_length': len(response),
            'response_preview': response[:200] + "..." if len(response) > 200 else response,
            'ai_model': 'Gemini 1.5 Pro',
            'features': ['Conversational responses', 'Context awareness', 'Personalized help']
        })
    except Exception as e:
        return jsonify({
            'status': 'AI Error - Falling back to pattern matching',
            'error': str(e),
            'fallback': 'Smart pattern matching active with improved conversational responses',
            'setup_guide': 'Check AI_SETUP.md for API key setup'
        })


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
