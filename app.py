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

from db_init import init_database

# Initialize database if it doesn't exist
if not os.path.exists('unihelp.db'):
    init_database()

# Database helper functions
def get_db_connection():
    """Return the Supabase client"""
    return db

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

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

# ==================== DEBUG ROUTE (TEMPORARY) ====================
@app.route('/debug')
def debug():
    """Debug route to check Supabase connection"""
    from supabase_client import db
    from werkzeug.security import check_password_hash
    import os
    
    # Check raw environment variables
    supabase_url = os.getenv('SUPABASE_URL', 'NOT_SET')
    supabase_key = os.getenv('SUPABASE_KEY', 'NOT_SET')
    
    admin = db.get_user_by_email('admin@unihelp.com')
    password_ok = check_password_hash(admin['passwordhash'], 'admin123') if admin else False
    
    return {
        'admin_exists': admin is not None,
        'email': admin['email'] if admin else 'Not found',
        'is_approved': admin['isapproved'] if admin else False,
        'password_matches': password_ok,
        'supabase_connected': db.client is not None,
        'userid': admin.get('userid') if admin else None,
        'DEBUG_env_check': {
            'SUPABASE_URL_loaded': supabase_url != 'NOT_SET',
            'SUPABASE_URL_value': supabase_url[:20] + '...' if supabase_url != 'NOT_SET' else 'NOT_SET',
            'SUPABASE_KEY_loaded': supabase_key != 'NOT_SET',
            'SUPABASE_KEY_length': len(supabase_key) if supabase_key != 'NOT_SET' else 0,
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

def auto_assign_ticket(conn, ticket_id, category):
    """
    Automatically assign ticket to the best available technician
    Returns technician info if assigned, None otherwise
    """
    # Get available technicians with their current workload
    technicians = conn.execute('''
        SELECT u.userid, u.name, u.email,
               COUNT(t.ticketid) as active_tickets,
               p.status as online_status,
               p.last_seen
        FROM user u
        LEFT JOIN ticket t ON u.userid = t.assignedto AND t.status IN ('Open', 'In Progress')
        LEFT JOIN user_presence p ON u.userid = p.userid
        WHERE u.role = 'technician' 
        AND u.isapproved = 1
        GROUP BY u.userid, u.name, u.email, p.status, p.last_seen
        ORDER BY 
            -- Prioritize online technicians
            CASE WHEN p.status = 'online' THEN 1 ELSE 0 END DESC,
            -- Then by workload (least busy first)
            COUNT(t.ticketid) ASC,
            -- Then by recent activity
            p.last_seen DESC
    ''').fetchall()
    
    # Find the best technician
    best_technician = None
    for tech in technicians:
        # Skip if offline and has been offline for more than 1 hour
        if tech['online_status'] != 'online':
            if tech['last_seen']:
                last_seen = datetime.fromisoformat(tech['last_seen'])
                if (datetime.now() - last_seen).total_seconds() > 3600:  # 1 hour
                    continue
            else:
                continue
        
        # Check if technician has capacity (max 5 active tickets)
        if tech['active_tickets'] < 5:
            best_technician = tech
            break
    
    # Assign ticket if we found a suitable technician
    if best_technician:
        conn.execute('''
            UPDATE ticket 
            SET assignedto = ?, status = 'In Progress', updatedat = CURRENT_TIMESTAMP
            WHERE ticketid = ?
        ''', (best_technician['userid'], ticket_id))
        
        # Log the assignment
        print(f"Auto-assigned ticket {ticket_id} to {best_technician['name']} (workload: {best_technician['active_tickets']})")
        
        return best_technician
    
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
    # Get ticket details from Supabase
    ticket = db.get_ticket_by_id(ticket_id)
    
    if not ticket:
        flash('Ticket not found', 'error')
        return redirect(url_for('dashboard'))
    
    # Authorization check
    role = session.get('role')
    user_id = session.get('user_id')
    
    if role not in ['admin'] and ticket['userid'] != user_id and ticket['assignedto'] != user_id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # NEW: Only fetch comments for staff, technicians, and admin (NOT students)
    comments = []
    can_comment = role in ['admin', 'technician', 'staff']
    
    if can_comment:
        comments = db.get_comments_by_ticket(ticket_id)
    
    return render_template('view_ticket.html', 
                         ticket=ticket, 
                         comments=comments,
                         can_comment=can_comment)

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
    
    # Authorization: Admin can comment on any ticket, others only on their own or assigned tickets
    if role not in ['admin'] and ticket['userid'] != user_id and ticket['assignedto'] != user_id:
        flash('Access denied', 'error')
        return redirect(url_for('dashboard'))
    
    # Add comment using Supabase
    db.create_comment({
        'content': content,
        'ticketid': ticket_id,
        'userid': user_id
    })
    
    flash('Comment added successfully', 'success')
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

    # Check if there's an active session (get all and filter)
    all_sessions = db.get_all_chat_sessions() if hasattr(db, 'get_all_chat_sessions') else []
    active_session = None
    
    # Since we don't have a direct method, let's use the client directly
    if db.client:
        response = db.client.table('chat_session').select('*').eq('userid', session.get('user_id')).eq('status', 'active').order('created_at', desc=True).limit(1).execute()
        active_session = response.data[0] if response.data else None
    
    if active_session:
        session_id = active_session['sessionid']
    else:
        # Create new session
        import uuid
        new_session_id = str(uuid.uuid4())
        new_session = db.create_chat_session({
            'sessionid': new_session_id,
            'userid': session.get('user_id'),
            'status': 'active'
        })
        session_id = new_session_id if new_session else None

    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Chat session started'
    })

@app.route('/api/chat/message', methods=['POST'])
@login_required
def send_chat_message():
    """Handle user message and generate bot response"""
    data = request.get_json()
    session_id = data.get('session_id')
    user_message = data.get('message', '').strip()
    
    if not user_message or not session_id:
        return jsonify({'success': False, 'error': 'Invalid data'}), 400
    
    # Verify session belongs to user
    chat_session = db.get_chat_session_by_id(session_id)
    
    if not chat_session or chat_session['userid'] != session.get('user_id') or chat_session['status'] != 'active':
        return jsonify({'success': False, 'error': 'Invalid session'}), 403
    
    # Save user message
    db.create_chat_message({
        'sessionid': session_id,
        'sender': 'user',
        'message': user_message
    })
    
    # Count messages in this session
    all_messages = db.get_chat_messages_by_session(session_id)
    message_count = len(all_messages)
    
    # Generate bot response
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
    
    return jsonify({
        'success': True,
        'bot_message': bot_response,
        'message_count': message_count,
        'should_escalate': should_escalate
    })

@app.route('/api/chat/request_technician_chat', methods=['POST'])
@login_required
def request_technician_chat():
    """Request live chat with technician and notify them"""
    
    data = request.get_json()
    session_id = data.get('session_id')
    
    # Get chat session
    chat_session = db.get_chat_session_by_id(session_id)
    
    if not chat_session or chat_session['userid'] != session.get('user_id'):
        return jsonify({'success': False, 'error': 'Invalid session'}), 403
    
    # Get user info
    user = db.get_user_by_id(session.get('user_id'))
    
    # Find available technician - more lenient for staff/admin
    user_role = session.get('role')
    time_window = 10 if user_role in ['staff', 'admin'] else 2  # minutes
    
    available_tech = db.get_available_technician(time_window)
    
    if available_tech:
        import uuid
        live_chat_id = str(uuid.uuid4())
        
        # Create live chat
        new_chat = db.create_live_chat({
            'livechatid': live_chat_id,
            'sessionid': session_id,
            'technicianid': available_tech['userid'],
            'status': 'active'
        })
        
        # Update session status
        if db.client:
            db.client.table('chat_session').update({'status': 'live_chat'}).eq('sessionid', session_id).execute()
        
        # Add system message with user info
        system_msg = f"🎯 Connected to {available_tech['name']} (Technician)\n\n📋 User Info:\n- Name: {user['name']}\n- Role: {user['role']}\n\nYou can now chat in real-time!"
        
        db.create_chat_message({
            'sessionid': session_id,
            'sender': 'bot',
            'message': system_msg,
            'intent': 'system'
        })
        
        # Send notification to technician (store in notifications table if exists)
        # Or you can use email/websocket here
        notification_msg = f"New chat request from {user['name']} ({user['role']}). Click to accept."
        
        return jsonify({
            'success': True,
            'type': 'live_chat',
            'technician_name': available_tech['name'],
            'technician_id': available_tech['userid'],
            'live_chat_id': live_chat_id,
            'message': f'✅ Connected to {available_tech["name"]}! Chat starting now...'
        })
    else:
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
    
    data = request.get_json()
    session_id = data.get('session_id')
    
    conn = get_db_connection()
    
    # Verify session
    chat_session = conn.execute('''
        SELECT * FROM chat_session WHERE sessionid = ? AND userid = ?
    ''', (session_id, session.get('user_id'))).fetchone()
    
    if not chat_session:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid session'}), 403
    
    # Find available technician
    two_minutes_ago = (datetime.now() - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
    
    available_tech = conn.execute('''
        SELECT u.userid, u.name
        FROM user u
        JOIN user_presence p ON u.userid = p.userid
        LEFT JOIN live_chat lc ON u.userid = lc.technicianid AND lc.status = 'active'
        WHERE u.role = 'technician'
        AND u.isapproved = 1
        AND p.status = 'online'
        AND p.last_seen > ?
        AND lc.livechatid IS NULL
        ORDER BY p.last_seen DESC
        LIMIT 1
    ''', (two_minutes_ago,)).fetchone()
    
    if available_tech:
        # Create live chat session
        cursor = conn.execute('''
            INSERT INTO live_chat (sessionid, technicianid, status)
            VALUES (?, ?, 'active')
        ''', (session_id, available_tech['userid']))
        
        live_chat_id = cursor.lastrowid
        
        # Update chat session status
        conn.execute('''
            UPDATE chat_session SET status = 'live_chat' WHERE sessionid = ?
        ''', (session_id,))
        
        # Add system message
        conn.execute('''
            INSERT INTO chat_message (sessionid, sender, message, intent)
            VALUES (?, 'bot', ?, 'system')
        ''', (session_id, f'🎯 Connected to {available_tech["name"]} (Technician). You can now chat in real-time!'))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'type': 'live_chat',
            'technician_name': available_tech['name'],
            'technician_id': available_tech['userid'],
            'live_chat_id': live_chat_id,
            'message': f'Connected to {available_tech["name"]}! You can now chat directly.'
        })
    else:
        conn.close()
        return jsonify({
            'success': True,
            'type': 'no_availability',
            'message': 'No technicians are currently online. Would you like to create a support ticket instead?'
        })

@app.route('/api/chat/escalate', methods=['POST'])
@login_required
def escalate_to_ticket():
    """Create ticket from chat session"""
    data = request.get_json()
    session_id = data.get('session_id')
    category = data.get('category', 'Other')
    
    conn = get_db_connection()
    
    # Get chat session
    chat_session = conn.execute('''
        SELECT * FROM chat_session WHERE sessionid = ? AND userid = ?
    ''', (session_id, session.get('user_id'))).fetchone()
    
    if not chat_session:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid session'}), 403
    
    # Get chat messages
    messages = conn.execute('''
        SELECT * FROM chat_message 
        WHERE sessionid = ? 
        ORDER BY created_at ASC
    ''', (session_id,)).fetchall()
    
    # Build ticket description from chat history
    chat_transcript = "=== Chat Transcript ===\\n\\n"
    for msg in messages:
        sender = "You" if msg['sender'] == 'user' else "Bot"
        chat_transcript += f"{sender}: {msg['message']}\\n\\n"
    
    chat_transcript += "=== End of Chat ===\\n\\nThis ticket was created from an unresolved chat session."
    
    # Extract main issue from first user message
    first_user_msg = messages['message'] if messages else "Issue reported via chat"
    title = first_user_msg[:100] + "..." if len(first_user_msg) > 100 else first_user_msg
    
    # Create ticket
    cursor = conn.execute('''
        INSERT INTO ticket (title, description, category, userid, status)
        VALUES (?, ?, ?, ?, 'Open')
    ''', (f"[Chat Escalation] {title}", chat_transcript, category, session.get('user_id')))
    
    ticket_id = cursor.lastrowid
    
    # Update chat session
    conn.execute('''
        UPDATE chat_session 
        SET status = 'escalated', escalated_ticket_id = ?, resolved_at = CURRENT_TIMESTAMP
        WHERE sessionid = ?
    ''', (ticket_id, session_id))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'ticket_id': ticket_id,
        'message': 'Ticket created successfully. A technician will assist you soon.'
    })

@app.route('/api/chat/history/<int:session_id>')
@login_required
def get_chat_history(session_id):
    """Get chat history for a session"""
    conn = get_db_connection()
    
    # Verify session belongs to user
    chat_session = conn.execute('''
        SELECT * FROM chat_session WHERE sessionid = ? AND userid = ?
    ''', (session_id, session.get('user_id'))).fetchone()
    
    if not chat_session:
        conn.close()
        return jsonify({'success': False, 'error': 'Invalid session'}), 403
    
    messages = conn.execute('''
        SELECT * FROM chat_message 
        WHERE sessionid = ? 
        ORDER BY created_at ASC
    ''', (session_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'messages': [dict(msg) for msg in messages],
        'status': chat_session['status']
    })


# ==================== ADMIN DIRECT MESSAGING ====================

@app.route('/admin/send_direct_message', methods=['POST'])
@login_required
@role_required(['admin'])
def admin_send_direct_message():
    """Admin sends direct message to technician WITHOUT chatbot escalation"""
    
    data = request.get_json()
    technician_id = data.get('technician_id')
    message = data.get('message', '').strip()
    ticket_id = data.get('ticket_id')  # Optional - link to ticket
    
    if not technician_id or not message:
        return jsonify({'success': False, 'error': 'Invalid request'}), 400
    
    conn = get_db_connection()
    
    # Verify technician exists and is approved
    tech = conn.execute('''
        SELECT * FROM user WHERE userid = ? AND role = 'technician' AND isapproved = 1
    ''', (technician_id,)).fetchone()
    
    if not tech:
        conn.close()
        return jsonify({'success': False, 'error': 'Technician not found'}), 404
    
    # Create a special admin message (not through chatbot)
    # Store in a separate or extended message system
    conn.execute('''
        INSERT INTO chat_message (sessionid, sender, message)
        VALUES (?, 'admin', ?)
    ''', (None, f"[ADMIN] {session.get('name')}: {message}"))
    
    conn.commit()
    conn.close()
    
    return jsonify({
        'success': True,
        'message': f'Message sent to {tech["name"]}'
    })

@app.route('/admin/technicians')
@login_required
@role_required(['admin'])
def admin_technicians():
    """View all technicians for direct messaging"""
    
    conn = get_db_connection()
    
    # Get all technicians with online status
    two_minutes_ago = (datetime.now() - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
    
    technicians = conn.execute('''
        SELECT u.userid, u.name, u.email, p.status, p.last_seen,
               COUNT(lc.livechatid) as active_chats
        FROM user u
        LEFT JOIN user_presence p ON u.userid = p.userid
        LEFT JOIN live_chat lc ON u.userid = lc.technicianid AND lc.status = 'active'
        WHERE u.role = 'technician' AND u.isapproved = 1
        GROUP BY u.userid
        ORDER BY p.last_seen DESC
    ''').fetchall()
    
    conn.close()
    
    return render_template('admin/technicians.html', technicians=technicians)

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
    conn = get_db_connection()
    
    # Format month for queries
    month_str = f"{year:04d}-{month:02d}"
    start_date = f"{month_str}-01"
    
    # Get next month for end date
    if month == 12:
        end_year = year + 1
        end_month = 1
    else:
        end_year = year
        end_month = month + 1
    end_date = f"{end_year:04d}-{end_month:02d}-01"
    
    # 1. Overall ticket statistics
    ticket_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 END) as resolved_tickets,
            COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_tickets,
            COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress_tickets,
            AVG(CASE WHEN resolvedat IS NOT NULL THEN 
                (julianday(resolvedat) - julianday(createdat)) * 24 END) as avg_resolution_hours,
            AVG(satisfaction_rating) as avg_satisfaction
        FROM ticket 
        WHERE createdat >= ? AND createdat < ?
    ''', (start_date, end_date)).fetchone()
    
    # 2. Tickets by category
    category_stats = conn.execute('''
        SELECT 
            category,
            COUNT(*) as total,
            COUNT(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 END) as resolved
        FROM ticket 
        WHERE createdat >= ? AND createdat < ?
        GROUP BY category
        ORDER BY total DESC
    ''', (start_date, end_date)).fetchall()
    
    # 3. Technician performance
    technician_stats = conn.execute('''
        SELECT 
            u.name as technician_name,
            u.email as technician_email,
            COUNT(t.ticketid) as tickets_assigned,
            COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END) as tickets_resolved,
            SUM(t.time_spent_hours) as total_hours_worked,
            AVG(CASE WHEN t.resolvedat IS NOT NULL THEN 
                (julianday(t.resolvedat) - julianday(t.createdat)) * 24 END) as avg_resolution_time,
            AVG(t.satisfaction_rating) as avg_satisfaction
        FROM user u
        LEFT JOIN ticket t ON u.userid = t.assignedto 
            AND t.createdat >= ? AND t.createdat < ?
        WHERE u.role = 'technician' AND u.isapproved = 1
        GROUP BY u.userid, u.name, u.email
        ORDER BY tickets_resolved DESC
    ''', (start_date, end_date)).fetchall()
    
    # 4. Work log hours by technician
    work_hours = conn.execute('''
        SELECT 
            u.name as technician_name,
            u.email as technician_email,
            SUM(w.hours_worked) as total_work_hours,
            COUNT(CASE WHEN w.work_type = 'ticket_resolution' THEN 1 END) as ticket_work_sessions,
            COUNT(CASE WHEN w.work_type = 'live_chat' THEN 1 END) as chat_sessions,
            COUNT(CASE WHEN w.work_type = 'maintenance' THEN 1 END) as maintenance_sessions
        FROM user u
        LEFT JOIN technician_work_log w ON u.userid = w.technicianid 
            AND w.start_time >= ? AND w.start_time < ?
        WHERE u.role = 'technician' AND u.isapproved = 1
        GROUP BY u.userid, u.name, u.email
        ORDER BY total_work_hours DESC
    ''', (start_date, end_date)).fetchall()
    
    # 5. Daily ticket creation trend
    daily_trend = conn.execute('''
        SELECT 
            DATE(createdat) as date,
            COUNT(*) as tickets_created,
            COUNT(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 END) as tickets_resolved
        FROM ticket 
        WHERE createdat >= ? AND createdat < ?
        GROUP BY DATE(createdat)
        ORDER BY date
    ''', (start_date, end_date)).fetchall()
    
    conn.close()
    
    return render_template('admin/monthly_report.html', 
                         year=year, 
                         month=month,
                         month_name=datetime(year, month, 1).strftime('%B'),
                         ticket_stats=ticket_stats,
                         category_stats=category_stats,
                         technician_stats=technician_stats,
                         work_hours=work_hours,
                         daily_trend=daily_trend)

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
    start_date = request.args.get('start_date', '2024-01-01')
    end_date = request.args.get('end_date', '2026-01-25')

    # Add one day to end_date to include the full end date
    end_date_plus_one = (datetime.strptime(end_date, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')

    conn = get_db_connection()

    # 1. Overall ticket statistics
    ticket_stats = conn.execute('''
        SELECT
            COUNT(*) as total_tickets,
            COUNT(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 END) as resolved_tickets,
            COUNT(CASE WHEN status = 'Open' THEN 1 END) as open_tickets,
            COUNT(CASE WHEN status = 'In Progress' THEN 1 END) as in_progress_tickets,
            AVG(CASE WHEN resolvedat IS NOT NULL THEN
                (julianday(resolvedat) - julianday(createdat)) * 24 END) as avg_resolution_hours,
            AVG(satisfaction_rating) as avg_satisfaction
        FROM ticket
        WHERE createdat >= ? AND createdat < ?
    ''', (start_date, end_date_plus_one)).fetchone()

    # 2. Tickets by category
    category_stats = conn.execute('''
        SELECT
            category,
            COUNT(*) as total,
            COUNT(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 END) as resolved
        FROM ticket
        WHERE createdat >= ? AND createdat < ?
        GROUP BY category
        ORDER BY total DESC
    ''', (start_date, end_date_plus_one)).fetchall()

    # 3. Technician performance
    technician_stats = conn.execute('''
        SELECT
            u.name as technician_name,
            u.email as technician_email,
            COUNT(t.ticketid) as tickets_assigned,
            COUNT(CASE WHEN t.status IN ('Resolved', 'Closed') THEN 1 END) as tickets_resolved,
            SUM(t.time_spent_hours) as total_hours_worked,
            AVG(CASE WHEN t.resolvedat IS NOT NULL THEN
                (julianday(t.resolvedat) - julianday(t.createdat)) * 24 END) as avg_resolution_time,
            AVG(t.satisfaction_rating) as avg_satisfaction
        FROM user u
        LEFT JOIN ticket t ON u.userid = t.assignedto
            AND t.createdat >= ? AND t.createdat < ?
        WHERE u.role = 'technician' AND u.isapproved = 1
        GROUP BY u.userid, u.name, u.email
        ORDER BY tickets_resolved DESC
    ''', (start_date, end_date_plus_one)).fetchall()

    # 4. Work log hours by technician
    work_hours = conn.execute('''
        SELECT
            u.name as technician_name,
            u.email as technician_email,
            SUM(w.hours_worked) as total_work_hours,
            COUNT(CASE WHEN w.work_type = 'ticket_resolution' THEN 1 END) as ticket_work_sessions,
            COUNT(CASE WHEN w.work_type = 'live_chat' THEN 1 END) as chat_sessions,
            COUNT(CASE WHEN w.work_type = 'maintenance' THEN 1 END) as maintenance_sessions
        FROM user u
        LEFT JOIN technician_work_log w ON u.userid = w.technicianid
            AND w.start_time >= ? AND w.start_time < ?
        WHERE u.role = 'technician' AND u.isapproved = 1
        GROUP BY u.userid, u.name, u.email
        ORDER BY total_work_hours DESC
    ''', (start_date, end_date_plus_one)).fetchall()

    # 5. Daily ticket creation trend
    daily_trend = conn.execute('''
        SELECT
            DATE(createdat) as date,
            COUNT(*) as tickets_created,
            COUNT(CASE WHEN status IN ('Resolved', 'Closed') THEN 1 END) as tickets_resolved
        FROM ticket
        WHERE createdat >= ? AND createdat < ?
        GROUP BY DATE(createdat)
        ORDER BY date
    ''', (start_date, end_date_plus_one)).fetchall()

    conn.close()

    # Format date range for display
    start_display = datetime.strptime(start_date, '%Y-%m-%d').strftime('%B %d, %Y')
    end_display = datetime.strptime(end_date, '%Y-%m-%d').strftime('%B %d, %Y')

    return render_template('admin/custom_report.html',
                         start_date=start_date,
                         end_date=end_date,
                         date_range=f"{start_display} - {end_display}",
                         ticket_stats=ticket_stats,
                         category_stats=category_stats,
                         technician_stats=technician_stats,
                         work_hours=work_hours,
                         daily_trend=daily_trend,
                         datetime=datetime)

# ==================== TECHNICIAN WORK LOGGING ====================

@app.route('/api/work/start', methods=['POST'])
@login_required
@role_required(['technician'])
def start_work_session():
    """Start a work session for technician"""
    data = request.get_json()
    work_type = data.get('work_type', 'other')
    ticket_id = data.get('ticket_id')
    description = data.get('description', '')

    if work_type not in ['ticket_resolution', 'live_chat', 'maintenance', 'other']:
        return jsonify({'success': False, 'error': 'Invalid work type'}), 400

    conn = get_db_connection()

    # Check if there's already an active session
    active_session = conn.execute('''
        SELECT * FROM technician_work_log 
        WHERE technicianid = ? AND end_time IS NULL
    ''', (session.get('user_id'),)).fetchone()

    if active_session:
        conn.close()
        return jsonify({'success': False, 'error': 'Active work session already exists'}), 400

    # Start new work session
    cursor = conn.execute('''
        INSERT INTO technician_work_log (technicianid, ticketid, work_type, start_time, description)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?)
    ''', (session.get('user_id'), ticket_id, work_type, description))

    worklog_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'worklog_id': worklog_id,
        'message': f'Work session started for {work_type}'
    })

@app.route('/api/work/end/<int:worklog_id>', methods=['POST'])
@login_required
@role_required(['technician'])
def end_work_session(worklog_id):
    """End a work session and calculate hours"""
    conn = get_db_connection()

    # Get the work session
    work_session = conn.execute('''
        SELECT * FROM technician_work_log 
        WHERE worklogid = ? AND technicianid = ? AND end_time IS NULL
    ''', (worklog_id, session.get('user_id'))).fetchone()

    if not work_session:
        conn.close()
        return jsonify({'success': False, 'error': 'Work session not found or already ended'}), 404

    # Calculate hours worked
    start_time = datetime.fromisoformat(work_session['start_time'])
    end_time = datetime.now()
    hours_worked = (end_time - start_time).total_seconds() / 3600

    # Update the session
    conn.execute('''
        UPDATE technician_work_log 
        SET end_time = CURRENT_TIMESTAMP, hours_worked = ?
        WHERE worklogid = ?
    ''', (hours_worked, worklog_id))

    # If this was ticket resolution, update ticket time_spent_hours
    if work_session['ticketid'] and work_session['work_type'] == 'ticket_resolution':
        conn.execute('''
            UPDATE ticket 
            SET time_spent_hours = COALESCE(time_spent_hours, 0) + ?, updatedat = CURRENT_TIMESTAMP
            WHERE ticketid = ?
        ''', (hours_worked, work_session['ticketid']))

    conn.commit()
    conn.close()

    return jsonify({
        'success': True,
        'hours_worked': round(hours_worked, 2),
        'message': f'Work session ended. {round(hours_worked, 2)} hours logged.'
    })

@app.route('/api/work/active')
@login_required
@role_required(['technician'])
def get_active_work_session():
    """Get current active work session for technician"""
    conn = get_db_connection()

    active_session = conn.execute('''
        SELECT * FROM technician_work_log 
        WHERE technicianid = ? AND end_time IS NULL
        ORDER BY start_time DESC LIMIT 1
    ''', (session.get('user_id'),)).fetchone()

    conn.close()

    if active_session:
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

@app.route('/technician/work_log')
@login_required
@role_required(['technician'])
def technician_work_log():
    """View technician's work log"""
    conn = get_db_connection()
    tech_id = session.get('user_id')

    # Get work sessions for current month
    current_month = datetime.now().strftime('%Y-%m')
    start_date = f"{current_month}-01"

    work_sessions = conn.execute('''
        SELECT * FROM technician_work_log 
        WHERE technicianid = ? AND start_time >= ?
        ORDER BY start_time DESC
    ''', (tech_id, start_date)).fetchall()

    # Calculate monthly totals
    monthly_stats = conn.execute('''
        SELECT 
            COUNT(*) as total_sessions,
            SUM(hours_worked) as total_hours,
            SUM(CASE WHEN work_type = 'ticket_resolution' THEN hours_worked ELSE 0 END) as ticket_hours,
            SUM(CASE WHEN work_type = 'live_chat' THEN hours_worked ELSE 0 END) as chat_hours,
            SUM(CASE WHEN work_type = 'maintenance' THEN hours_worked ELSE 0 END) as maintenance_hours
        FROM technician_work_log 
        WHERE technicianid = ? AND start_time >= ? AND end_time IS NOT NULL
    ''', (tech_id, start_date)).fetchone()

    conn.close()

    return render_template('technician/work_log.html', 
                         work_sessions=work_sessions,
                         monthly_stats=monthly_stats,
                         current_month=current_month)

# ==================== PRESENCE TRACKING ====================

@app.route('/api/presence/update', methods=['POST'])
@login_required
def update_presence():
    """Update user online status"""
    conn = get_db_connection()
    
    # SQLite doesn't support ON CONFLICT in older versions, so use INSERT OR REPLACE
    conn.execute('''
        INSERT OR REPLACE INTO user_presence (userid, status, last_seen)
        VALUES (?, 'online', CURRENT_TIMESTAMP)
    ''', (session.get('user_id'),))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/api/presence/technicians')
@login_required
def get_online_technicians():
    """Get list of online technicians"""
    conn = get_db_connection()
    
    # Get technicians online in last 2 minutes
    two_minutes_ago = (datetime.now() - timedelta(minutes=2)).strftime('%Y-%m-%d %H:%M:%S')
    
    technicians = conn.execute('''
        SELECT u.userid, u.name, u.email, p.status, p.last_seen
        FROM user u
        JOIN user_presence p ON u.userid = p.userid
        WHERE u.role = 'technician' 
        AND u.isapproved = 1
        AND p.status = 'online'
        AND p.last_seen > ?
        ORDER BY p.last_seen DESC
    ''', (two_minutes_ago,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'technicians': [dict(t) for t in technicians],
        'count': len(technicians)
    })

# ==================== LIVE CHAT HANDOFF ====================

@app.route('/api/chat/end_live_chat/<int:live_chat_id>', methods=['POST'])
@login_required
def end_live_chat(live_chat_id):
    """End live chat session"""
    conn = get_db_connection()
    
    conn.execute('''
        UPDATE live_chat 
        SET status = 'ended', ended_at = CURRENT_TIMESTAMP 
        WHERE livechatid = ?
    ''', (live_chat_id,))
    
    live_chat = conn.execute('''
        SELECT sessionid FROM live_chat WHERE livechatid = ?
    ''', (live_chat_id,)).fetchone()
    
    if live_chat:
        conn.execute('''
            UPDATE chat_session 
            SET status = 'resolved', resolved_at = CURRENT_TIMESTAMP 
            WHERE sessionid = ?
        ''', (live_chat['sessionid'],))
        
        conn.execute('''
            INSERT INTO chat_message (sessionid, sender, message, intent)
            VALUES (?, 'bot', ?, 'system')
        ''', (live_chat['sessionid'], '✅ Chat session ended. Thank you for using UniHelp!'))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Live chat ended'})

@app.route('/technician/live_chats')
@login_required
@role_required(['technician'])
def technician_live_chats():
    """View active live chat sessions"""
    conn = get_db_connection()
    tech_id = session.get('user_id')
    
    live_chats = conn.execute('''
        SELECT lc.*, cs.sessionid, u.name as user_name, u.email as user_email, u.role as user_role
        FROM live_chat lc
        JOIN chat_session cs ON lc.sessionid = cs.sessionid
        JOIN user u ON cs.userid = u.userid
        WHERE lc.technicianid = ? AND lc.status = 'active'
        ORDER BY lc.started_at DESC
    ''', (tech_id,)).fetchall()
    
    conn.close()
    
    return render_template('technician/live_chats.html', live_chats=live_chats)

@app.route('/api/chat/technician/send', methods=['POST'])
@login_required
@role_required(['technician'])
def technician_send_message():
    """Technician sends message in live chat"""
    data = request.get_json()
    session_id = data.get('session_id')
    message = data.get('message', '').strip()
    
    if not message:
        return jsonify({'success': False, 'error': 'Empty message'}), 400
    
    conn = get_db_connection()
    
    live_chat = conn.execute('''
        SELECT * FROM live_chat 
        WHERE sessionid = ? AND technicianid = ? AND status = 'active'
    ''', (session_id, session.get('user_id'))).fetchone()
    
    if not live_chat:
        conn.close()
        return jsonify({'success': False, 'error': 'Not authorized'}), 403
    
    conn.execute('''
        INSERT INTO chat_message (sessionid, sender, message)
        VALUES (?, 'technician', ?)
    ''', (session_id, message))
    
    conn.commit()
    conn.close()
    
    return jsonify({'success': True, 'message': 'Message sent'})

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
    conn = get_db_connection()
    messages = conn.execute('''
        SELECT sender, message FROM chat_message 
        WHERE sessionid = ? 
        ORDER BY created_at ASC
        LIMIT 15
    ''', (session_id,)).fetchall()
    conn.close()
    
    context = []
    for msg in messages:
        role = "user" if msg['sender'] == 'user' else "assistant"
        context.append({
            "role": role,
            "content": msg['message']
        })
    return context


def generate_ai_response(user_message, message_count, session_id):
    """Fast Gemini AI with UniHelp knowledge"""
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
        
        # Focused, efficient system prompt for IT support
        system_prompt = f"""You are an expert IT support specialist at a university helpdesk. Help users with technical issues naturally and efficiently.

USER INFO: {user_name} ({user_role}) - Message {message_count} in conversation

YOUR ROLE:
- Provide clear, step-by-step technical solutions
- Be friendly and professional like a real IT technician
- Ask for clarification when needed
- Know when to suggest creating a ticket or connecting to a technician
- Understand university IT systems and policies

KEY CAPABILITIES:
1. Hardware troubleshooting (computers, printers, peripherals)
2. Software issues (installation, configuration, errors)
3. Network problems (WiFi, internet, VPN)
4. Account access (passwords, login issues)
5. Email configuration and problems
6. University-specific systems and software

RESPONSE STYLE:
- Start with empathy: "I understand that can be frustrating..."
- Give the most likely solution first
- Number your steps clearly
- Ask "Did that resolve it?" to check
- Offer alternatives if first solution doesn't work
- End with escalation option if needed

ESCALATION: After 3-4 attempts or for complex issues, suggest: "Would you like me to connect you with a technician or create a support ticket?"

Be concise but thorough. Act like an experienced IT professional."""
        
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
        
        # Generate response with optimized settings
        response = model.generate_content(
            messages,
            generation_config=types.GenerationConfig(
                max_output_tokens=500,  # More focused responses
                temperature=0.6,  # More consistent, less random
                top_p=0.8,  # Focused responses
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
    """Get new chat requests for technician"""
    conn = get_db_connection()
    tech_id = session.get('user_id')
    
    # Get active live chats
    new_chats = conn.execute('''
        SELECT lc.livechatid, lc.sessionid, u.name, u.role, cs.created_at,
               (SELECT message FROM chat_message WHERE sessionid = cs.sessionid 
                ORDER BY created_at DESC LIMIT 1) as last_message
        FROM live_chat lc
        JOIN chat_session cs ON lc.sessionid = cs.sessionid
        JOIN user u ON cs.userid = u.userid
        WHERE lc.technicianid = ? AND lc.status = 'active'
        ORDER BY lc.started_at DESC
    ''', (tech_id,)).fetchall()
    
    conn.close()
    
    return jsonify({
        'success': True,
        'new_chats': [dict(chat) for chat in new_chats],
        'count': len(new_chats)
    })


@app.route('/technician/chat/<int:live_chat_id>', methods=['GET'])
@login_required
@role_required(['technician'])
def view_technician_chat(live_chat_id):
    """View specific chat as technician"""
    conn = get_db_connection()
    tech_id = session.get('user_id')
    
    live_chat = conn.execute('''
        SELECT lc.*, cs.sessionid, u.name as user_name, u.email as user_email
        FROM live_chat lc
        JOIN chat_session cs ON lc.sessionid = cs.sessionid
        JOIN user u ON cs.userid = u.userid
        WHERE lc.livechatid = ? AND lc.technicianid = ?
    ''', (live_chat_id, tech_id)).fetchone()
    
    if not live_chat:
        conn.close()
        return redirect(url_for('technician_dashboard'))
    
    # Get chat messages
    messages = conn.execute('''
        SELECT * FROM chat_message 
        WHERE sessionid = ? 
        ORDER BY created_at ASC
    ''', (live_chat['sessionid'],)).fetchall()
    
    conn.close()
    
    return render_template('technician/view_chat.html', 
                         live_chat=live_chat, 
                         messages=messages)

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
