# db_init.py
# Database Initialization Script for UniHelp IT Helpdesk Management System

import sqlite3
from werkzeug.security import generate_password_hash

def init_database():
    """Initialize the UniHelp database with all required tables and default admin user"""
    
    conn = sqlite3.connect('unihelp.db')
    cursor = conn.cursor()
    
    print("🔧 Initializing UniHelp Database...")
    
    # Create User Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            userid INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(100) NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            passwordhash VARCHAR(255) NOT NULL,
            role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'staff', 'technician', 'student')),
            isapproved BOOLEAN DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    print("✓ User table created")
    
    # Create Ticket Table with enhanced tracking
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket (
            ticketid INTEGER PRIMARY KEY AUTOINCREMENT,
            title VARCHAR(200) NOT NULL,
            description TEXT NOT NULL,
            category VARCHAR(50) NOT NULL,
            priority VARCHAR(20) DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent')),
            status VARCHAR(30) DEFAULT 'Open' CHECK(status IN ('Open', 'In Progress', 'Pending', 'Resolved', 'Closed', 'Reopened')),
            filepath VARCHAR(255),
            createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updatedat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolvedat TIMESTAMP,
            userid INTEGER NOT NULL,
            assignedto INTEGER,
            resolvedby INTEGER,
            time_spent_hours REAL DEFAULT 0,
            resolution_notes TEXT,
            satisfaction_rating INTEGER CHECK(satisfaction_rating >= 1 AND satisfaction_rating <= 5),
            FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE,
            FOREIGN KEY (assignedto) REFERENCES user(userid) ON DELETE SET NULL,
            FOREIGN KEY (resolvedby) REFERENCES user(userid) ON DELETE SET NULL
        )
    ''')
    print("✓ Enhanced ticket table created")
    
    # Create Comment Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS comment (
            commentid INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ticketid INTEGER NOT NULL,
            userid INTEGER NOT NULL,
            FOREIGN KEY (ticketid) REFERENCES ticket(ticketid) ON DELETE CASCADE,
            FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE
        )
    ''')
    print("✓ Comment table created")
    
    # Create Chat Session Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_session (
            sessionid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            resolved_at TIMESTAMP,
            escalated_ticket_id INTEGER,
            FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE,
            FOREIGN KEY (escalated_ticket_id) REFERENCES ticket(ticketid) ON DELETE SET NULL
        )
    ''')
    print("✓ Chat session table created")
    
    # Create Chat Message Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chat_message (
            messageid INTEGER PRIMARY KEY AUTOINCREMENT,
            sessionid INTEGER NOT NULL,
            sender VARCHAR(20) NOT NULL,
            message TEXT NOT NULL,
            intent VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sessionid) REFERENCES chat_session(sessionid) ON DELETE CASCADE
        )
    ''')
    print("✓ Chat message table created")
    
    # Create Chatbot Interaction Table (for future AI integration)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS chatbot_interaction (
            chatid INTEGER PRIMARY KEY AUTOINCREMENT,
            userid INTEGER NOT NULL,
            query TEXT NOT NULL,
            response TEXT NOT NULL,
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE
        )
    ''')
    print("✓ Chatbot interaction table created")
    
    # Create default admin user
    admin_password = generate_password_hash('admin123')
    try:
        cursor.execute('''
            INSERT INTO user (name, email, passwordhash, role, isapproved)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Admin User', 'admin@unihelp.com', admin_password, 'admin', 1))
        print("✓ Default admin user created")
        print("  📧 Email: admin@unihelp.com")
        print("  🔑 Password: admin123")
    except sqlite3.IntegrityError:
        print("✓ Admin user already exists")
    
    # Create sample technician (optional)
    try:
        tech_password = generate_password_hash('tech123')
        cursor.execute('''
            INSERT INTO user (name, email, passwordhash, role, isapproved)
            VALUES (?, ?, ?, ?, ?)
        ''', ('John Tech', 'tech@unihelp.com', tech_password, 'technician', 1))
        print("✓ Sample technician created")
        print("  📧 Email: tech@unihelp.com")
        print("  🔑 Password: tech123")
    except sqlite3.IntegrityError:
        print("✓ Sample technician already exists")
    
    # Create sample staff user (optional)
    try:
        staff_password = generate_password_hash('staff123')
        cursor.execute('''
            INSERT INTO user (name, email, passwordhash, role, isapproved)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Mary Staff', 'staff@unihelp.com', staff_password, 'staff', 1))
        print("✓ Sample staff user created")
        print("  📧 Email: staff@unihelp.com")
        print("  🔑 Password: staff123")
    except sqlite3.IntegrityError:
        print("✓ Sample staff user already exists")
    
    # Create sample student user (optional)
    try:
        student_password = generate_password_hash('student123')
        cursor.execute('''
            INSERT INTO user (name, email, passwordhash, role, isapproved)
            VALUES (?, ?, ?, ?, ?)
        ''', ('Alice Student', 'student@unihelp.com', student_password, 'student', 1))
        print("✓ Sample student user created")
        print("  📧 Email: student@unihelp.com")
        print("  🔑 Password: student123")
    except sqlite3.IntegrityError:
        print("✓ Sample student user already exists")
        
    # Add these table creations in your db_init.py, after the chatbot_interaction table

# Create User Presence Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_presence (
            userid INTEGER PRIMARY KEY,
            status VARCHAR(20) DEFAULT 'offline',
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE
        )
    ''')
    print("✓ User presence table created")

# Create Live Chat Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS live_chat (
            livechatid INTEGER PRIMARY KEY AUTOINCREMENT,
            sessionid INTEGER NOT NULL,
            technicianid INTEGER NOT NULL,
            status VARCHAR(20) DEFAULT 'active',
            started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            ended_at TIMESTAMP,
            FOREIGN KEY (sessionid) REFERENCES chat_session(sessionid) ON DELETE CASCADE,
            FOREIGN KEY (technicianid) REFERENCES user(userid) ON DELETE CASCADE
        )
    ''')
    print("✓ Live chat table created")

    # Create Technician Work Log Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS technician_work_log (
            worklogid INTEGER PRIMARY KEY AUTOINCREMENT,
            technicianid INTEGER NOT NULL,
            ticketid INTEGER,
            work_type VARCHAR(50) NOT NULL CHECK(work_type IN ('ticket_resolution', 'live_chat', 'maintenance', 'other')),
            start_time TIMESTAMP NOT NULL,
            end_time TIMESTAMP,
            hours_worked REAL,
            description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (technicianid) REFERENCES user(userid) ON DELETE CASCADE,
            FOREIGN KEY (ticketid) REFERENCES ticket(ticketid) ON DELETE SET NULL
        )
    ''')
    print("✓ Technician work log table created")

    # Create Ticket History Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS ticket_history (
            historyid INTEGER PRIMARY KEY AUTOINCREMENT,
            ticketid INTEGER NOT NULL,
            changed_by INTEGER NOT NULL,
            old_status VARCHAR(30),
            new_status VARCHAR(30) NOT NULL,
            old_assignedto INTEGER,
            new_assignedto INTEGER,
            change_reason TEXT,
            changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (ticketid) REFERENCES ticket(ticketid) ON DELETE CASCADE,
            FOREIGN KEY (changed_by) REFERENCES user(userid) ON DELETE CASCADE,
            FOREIGN KEY (old_assignedto) REFERENCES user(userid) ON DELETE SET NULL,
            FOREIGN KEY (new_assignedto) REFERENCES user(userid) ON DELETE SET NULL
        )
    ''')
    print("✓ Ticket history table created")

    # Create Monthly Reports Cache Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS monthly_reports_cache (
            reportid INTEGER PRIMARY KEY AUTOINCREMENT,
            report_month VARCHAR(7) NOT NULL, -- Format: YYYY-MM
            report_type VARCHAR(50) NOT NULL,
            report_data TEXT NOT NULL, -- JSON data
            generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(report_month, report_type)
        )
    ''')
    print("✓ Monthly reports cache table created")
    conn.commit()
    conn.close()
    
    print("\n✅ Database initialized successfully!")
    print("\n📝 Quick Start:")
    print("   1. Run: python app.py")
    print("   2. Visit: http://localhost:5000")
    print("   3. Login with admin credentials")
    print("\n🔒 Remember to change default passwords in production!")

if __name__ == '__main__':
    init_database()
