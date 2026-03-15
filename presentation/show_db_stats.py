# show_db_stats.py
# Database Statistics and Visualization for Presentation
# Updated to support both SQLite (local) and Supabase (production)

import os
import sys
from datetime import datetime

# Add parent directory to path to import supabase_client
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    from supabase_client import db
    SUPABASE_AVAILABLE = db.client is not None
except:
    SUPABASE_AVAILABLE = False
    print("⚠️  Supabase not available, falling back to SQLite")

# Only import sqlite3 if Supabase is not available
if not SUPABASE_AVAILABLE:
    import sqlite3


def print_section_header(title):
    """Print a formatted section header"""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_subsection(title):
    """Print a subsection header"""
    print(f"\n📌 {title}")
    print("-" * 60)


def show_database_stats_supabase():
    """Display comprehensive database statistics using Supabase"""
    
    print_section_header("📊 UNIHELP DATABASE STATISTICS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # 1. User Statistics
        print_subsection("👥 USER MANAGEMENT")
        
        # Get users by role
        response = db.client.table('user').select('*').execute()
        users = response.data
        
        # Count by role
        role_counts = {}
        for user in users:
            role = user.get('role', 'unknown')
            role_counts[role] = role_counts.get(role, 0) + 1
        
        print("\nUsers by Role:")
        for role, count in sorted(role_counts.items()):
            print(f"  • {role.capitalize():15} : {count:3} users")
        
        total_users = len(users)
        print(f"\n  Total Users: {total_users}")
        
        # Show all users
        print("\nUser Directory:")
        for user in sorted(users, key=lambda x: (x.get('role', ''), x.get('created_at', ''))):
            uid = user.get('userid', 'N/A')
            name = user.get('name', 'Unknown')
            email = user.get('email', 'N/A')
            role = user.get('role', 'unknown')
            approved = user.get('isapproved', False)
            status = "✓ Approved" if approved else "⏳ Pending"
            print(f"  [{role.upper():12}] {name:20} | {email:30} | {status}")
        
        # 2. Ticket Statistics
        print_subsection("🎫 TICKET MANAGEMENT")
        
        response = db.client.table('ticket').select('*').execute()
        tickets = response.data
        
        # Count by status
        status_counts = {}
        for ticket in tickets:
            status = ticket.get('status', 'Unknown')
            status_counts[status] = status_counts.get(status, 0) + 1
        
        print("\nTickets by Status:")
        for status, count in sorted(status_counts.items()):
            print(f"  • {status:15} : {count:3} tickets")
        
        total_tickets = len(tickets)
        print(f"\n  Total Tickets: {total_tickets}")
        
        # Priority distribution
        priority_counts = {}
        for ticket in tickets:
            priority = ticket.get('priority', 'Unknown')
            priority_counts[priority] = priority_counts.get(priority, 0) + 1
        
        print("\nTickets by Priority:")
        for priority, count in sorted(priority_counts.items()):
            bar = "█" * min(count, 20)  # Limit bar length
            print(f"  • {priority:8} : {count:2} {bar}")
        
        # Category distribution
        category_counts = {}
        for ticket in tickets:
            category = ticket.get('category', 'Unknown')
            category_counts[category] = category_counts.get(category, 0) + 1
        
        print("\nTickets by Category (Top 5):")
        top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        for category, count in top_categories:
            print(f"  • {category:20} : {count:3} tickets")
        
        # Resolution stats
        resolved_tickets = [t for t in tickets if t.get('resolvedby') is not None]
        resolved_count = len(resolved_tickets)
        
        if resolved_count > 0:
            print(f"\n  Resolved Tickets: {resolved_count}")
        
        # Satisfaction ratings
        rated_tickets = [t for t in tickets if t.get('satisfaction_rating') is not None]
        if rated_tickets:
            avg_rating = sum(t['satisfaction_rating'] for t in rated_tickets) / len(rated_tickets)
            positive = sum(1 for t in rated_tickets if t['satisfaction_rating'] >= 4)
            negative = sum(1 for t in rated_tickets if t['satisfaction_rating'] <= 2)
            
            stars = "⭐" * int(avg_rating)
            print(f"\n  Average Satisfaction: {avg_rating:.1f}/5.0 {stars}")
            print(f"  Positive Reviews (4-5★): {positive}")
            print(f"  Negative Reviews (1-2★): {negative}")
        
        # 3. Chat Statistics
        print_subsection("💬 CHAT & AI INTERACTIONS")
        
        chat_sessions = len(db.client.table('chat_session').select('*').execute().data)
        chat_messages = len(db.client.table('chat_message').select('*').execute().data)
        live_chats = len(db.client.table('live_chat').select('*').execute().data)
        bot_interactions = len(db.client.table('chatbot_interaction').select('*').execute().data)
        
        print(f"\n  Chat Sessions: {chat_sessions}")
        print(f"  Chat Messages: {chat_messages}")
        print(f"  Live Chats with Technicians: {live_chats}")
        print(f"  AI Bot Interactions: {bot_interactions}")
        
        # Chat session status
        response = db.client.table('chat_session').select('*').execute()
        chat_statuses = {}
        for session in response.data:
            status = session.get('status', 'Unknown')
            chat_statuses[status] = chat_statuses.get(status, 0) + 1
        
        if chat_statuses:
            print("\n  Chat Session Status:")
            for status, count in sorted(chat_statuses.items()):
                print(f"    • {status:15} : {count:3}")
        
        # 4. Technician Work Stats
        print_subsection("🔧 TECHNICIAN PERFORMANCE")
        
        work_logs = len(db.client.table('technician_work_log').select('*').execute().data)
        print(f"\n  Total Work Log Entries: {work_logs}")
        
        # 5. Audit Trail
        print_subsection("📋 AUDIT TRAIL")
        
        history_count = len(db.client.table('ticket_history').select('*').execute().data)
        print(f"\n  Total Status Changes Tracked: {history_count}")
        
        # 6. Recent Activity
        print_subsection("🕐 RECENT ACTIVITY (Last 10 Tickets)")
        
        response = db.client.table('ticket').select('*').order('createdat', desc=True).limit(10).execute()
        recent = response.data
        
        if recent:
            print(f"\n  {'ID':4} | {'Title':30} | {'Creator':15} | {'Status':12} | {'Date'}")
            print("  " + "-" * 90)
            for ticket in recent:
                tid = ticket.get('ticketid', 'N/A')
                title = ticket.get('title', 'Untitled')
                status = ticket.get('status', 'Unknown')
                date = ticket.get('createdat', 'Unknown')[:10]
                
                short_title = title[:28] + ".." if len(title) > 30 else title
                print(f"  {tid:4} | {short_title:30} | {'Creator':15} | {status:12} | {date}")
        
        # Final Summary
        print_section_header("✅ SUMMARY")
        
        print(f"""
  👥 Total Users           : {total_users}
  🎫 Total Tickets         : {total_tickets}
  💬 Chat Sessions         : {chat_sessions}
  🔧 Work Log Entries      : {work_logs}
  📋 Audit Trail Entries   : {history_count}
  
  System Status: OPERATIONAL ✅
  """)
        
        print("=" * 60)
        print("Database statistics generated successfully!")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error fetching statistics: {e}")
        import traceback
        traceback.print_exc()


def show_database_stats_sqlite():
    """Display comprehensive database statistics using SQLite"""
    
    # Try multiple paths to find the database
    possible_paths = [
        'unihelp.db',  # Current directory
        '../unihelp.db',  # Parent directory (when running from presentation folder)
        os.path.join(os.path.dirname(__file__), '..', 'unihelp.db'),  # Script's parent directory
    ]
    
    db_path = None
    for path in possible_paths:
        if os.path.exists(path):
            db_path = path
            break
    
    if not db_path:
        print("❌ Error: unihelp.db not found!")
        print("\nSearched in:")
        for path in possible_paths:
            print(f"  - {path}")
        print("\n💡 Solution:")
        print("   1. Make sure you're in the UniHelp folder")
        print("   2. Run: python db_init.py")
        print("   3. Then run this script again")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    print_section_header("📊 UNIHELP DATABASE STATISTICS")
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # 1. User Statistics
    print_subsection("👥 USER MANAGEMENT")
    
    cursor.execute('''
        SELECT role, COUNT(*) as count 
        FROM user 
        GROUP BY role
    ''')
    roles = cursor.fetchall()
    
    print("\nUsers by Role:")
    for role, count in roles:
        print(f"  • {role.capitalize():15} : {count:3} users")
    
    total_users = sum(count for _, count in roles)
    print(f"\n  Total Users: {total_users}")
    
    # Show all users
    cursor.execute('SELECT userid, name, email, role, isapproved, created_at FROM user ORDER BY role, created_at')
    users = cursor.fetchall()
    
    print("\nUser Directory:")
    for user in users:
        uid, name, email, role, approved, created = user
        status = "✓ Approved" if approved else "⏳ Pending"
        print(f"  [{role.upper():12}] {name:20} | {email:30} | {status}")
    
    # 2. Ticket Statistics
    print_subsection("🎫 TICKET MANAGEMENT")
    
    cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM ticket 
        GROUP BY status
    ''')
    statuses = cursor.fetchall()
    
    print("\nTickets by Status:")
    for status, count in statuses:
        print(f"  • {status:15} : {count:3} tickets")
    
    total_tickets = sum(count for _, count in statuses)
    print(f"\n  Total Tickets: {total_tickets}")
    
    # Priority distribution
    cursor.execute('''
        SELECT priority, COUNT(*) as count 
        FROM ticket 
        GROUP BY priority
    ''')
    priorities = cursor.fetchall()
    
    print("\nTickets by Priority:")
    for priority, count in priorities:
        bar = "█" * count
        print(f"  • {priority:8} : {count:2} {bar}")
    
    # Category distribution
    cursor.execute('''
        SELECT category, COUNT(*) as count 
        FROM ticket 
        GROUP BY category
        ORDER BY count DESC
    ''')
    categories = cursor.fetchall()
    
    print("\nTickets by Category (Top 5):")
    for category, count in categories[:5]:
        print(f"  • {category:20} : {count:3} tickets")
    
    # Resolution stats
    cursor.execute('''
        SELECT 
            COUNT(CASE WHEN resolvedby IS NOT NULL THEN 1 END) as resolved,
            AVG(CASE WHEN resolvedat IS NOT NULL 
                THEN JULIANDAY(resolvedat) - JULIANDAY(createdat) 
                END) as avg_resolution_days
        FROM ticket
    ''')
    resolved, avg_days = cursor.fetchone()
    
    if avg_days:
        print(f"\n  Resolved Tickets: {resolved}")
        print(f"  Avg Resolution Time: {avg_days:.2f} days")
    
    # Satisfaction ratings
    cursor.execute('''
        SELECT 
            AVG(satisfaction_rating) as avg_rating,
            COUNT(CASE WHEN satisfaction_rating >= 4 THEN 1 END) as positive,
            COUNT(CASE WHEN satisfaction_rating <= 2 THEN 1 END) as negative
        FROM ticket
        WHERE satisfaction_rating IS NOT NULL
    ''')
    avg_rating, positive, negative = cursor.fetchone()
    
    if avg_rating:
        stars = "⭐" * int(avg_rating)
        print(f"\n  Average Satisfaction: {avg_rating:.1f}/5.0 {stars}")
        print(f"  Positive Reviews (4-5★): {positive}")
        print(f"  Negative Reviews (1-2★): {negative}")
    
    # 3. Chat Statistics
    print_subsection("💬 CHAT & AI INTERACTIONS")
    
    def get_table_count(cursor, table_name):
        cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
        return cursor.fetchone()[0]
    
    chat_sessions = get_table_count(cursor, 'chat_session')
    chat_messages = get_table_count(cursor, 'chat_message')
    live_chats = get_table_count(cursor, 'live_chat')
    bot_interactions = get_table_count(cursor, 'chatbot_interaction')
    
    print(f"\n  Chat Sessions: {chat_sessions}")
    print(f"  Chat Messages: {chat_messages}")
    print(f"  Live Chats with Technicians: {live_chats}")
    print(f"  AI Bot Interactions: {bot_interactions}")
    
    # Chat session status
    cursor.execute('''
        SELECT status, COUNT(*) as count 
        FROM chat_session 
        GROUP BY status
    ''')
    chat_statuses = cursor.fetchall()
    
    if chat_statuses:
        print("\n  Chat Session Status:")
        for status, count in chat_statuses:
            print(f"    • {status:15} : {count:3}")
    
    # 4. Technician Work Stats
    print_subsection("🔧 TECHNICIAN PERFORMANCE")
    
    work_logs = get_table_count(cursor, 'technician_work_log')
    
    cursor.execute('''
        SELECT 
            u.name,
            COUNT(t.ticketid) as tickets_resolved,
            COALESCE(SUM(wl.hours_worked), 0) as total_hours
        FROM user u
        LEFT JOIN ticket t ON u.userid = t.resolvedby
        LEFT JOIN technician_work_log wl ON u.userid = wl.technicianid
        WHERE u.role = 'technician'
        GROUP BY u.userid, u.name
        ORDER BY tickets_resolved DESC
    ''')
    tech_stats = cursor.fetchall()
    
    print(f"\n  Total Work Log Entries: {work_logs}")
    
    if tech_stats:
        print("\n  Technician Performance:")
        for name, tickets, hours in tech_stats:
            print(f"    • {name:20} : {tickets:2} tickets resolved, {hours:5.1f} hours logged")
    
    # 5. Audit Trail
    print_subsection("📋 AUDIT TRAIL")
    
    history_count = get_table_count(cursor, 'ticket_history')
    print(f"\n  Total Status Changes Tracked: {history_count}")
    
    if history_count > 0:
        cursor.execute('''
            SELECT 
                u.name,
                COUNT(h.historyid) as changes_made
            FROM ticket_history h
            JOIN user u ON h.changed_by = u.userid
            GROUP BY u.userid, u.name
            ORDER BY changes_made DESC
            LIMIT 5
        ''')
        top_editors = cursor.fetchall()
        
        print("\n  Most Active Users (Status Changes):")
        for name, changes in top_editors:
            print(f"    • {name:20} : {changes:3} changes")
    
    # 6. Recent Activity
    print_subsection("🕐 RECENT ACTIVITY (Last 10 Tickets)")
    
    cursor.execute('''
        SELECT 
            t.ticketid,
            t.title,
            u.name as creator,
            t.status,
            t.createdat
        FROM ticket t
        JOIN user u ON t.userid = u.userid
        ORDER BY t.createdat DESC
        LIMIT 10
    ''')
    recent = cursor.fetchall()
    
    if recent:
        print(f"\n  {'ID':4} | {'Title':30} | {'Creator':15} | {'Status':12} | {'Date'}")
        print("  " + "-" * 90)
        for ticket in recent:
            tid, title, creator, status, date = ticket
            short_title = title[:28] + ".." if len(title) > 30 else title
            short_creator = creator[:15] + "." if len(creator) > 15 else creator
            print(f"  {tid:4} | {short_title:30} | {short_creator:15} | {status:12} | {date[:10]}")
    
    # 7. Storage Info
    print_subsection("💾 DATABASE STORAGE")
    
    db_size = os.path.getsize(db_path)
    db_size_kb = db_size / 1024
    db_size_mb = db_size_kb / 1024
    
    print(f"\n  Database File: unihelp.db")
    print(f"  File Size: {db_size_mb:.2f} MB ({db_size_kb:.1f} KB)")
    
    # Table sizes
    cursor.execute('''
        SELECT name FROM sqlite_master WHERE type='table'
    ''')
    tables = cursor.fetchall()
    
    print(f"\n  Tables in Database: {len(tables)}")
    print("  Tables: ", end="")
    table_names = [table[0] for table in tables]
    print(", ".join(table_names))
    
    # Final Summary
    print_section_header("✅ SUMMARY")
    
    print(f"""
  👥 Total Users           : {total_users}
  🎫 Total Tickets         : {total_tickets}
  💬 Chat Sessions         : {chat_sessions}
  🔧 Work Log Entries      : {work_logs}
  📋 Audit Trail Entries   : {history_count}
  💾 Database Size         : {db_size_mb:.2f} MB
  
  System Status: OPERATIONAL ✅
  """)
    
    conn.close()
    
    print("=" * 60)
    print("Database statistics generated successfully!")
    print("=" * 60 + "\n")


if __name__ == '__main__':
    try:
        show_database_stats()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
