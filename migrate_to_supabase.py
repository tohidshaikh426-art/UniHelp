# migrate_to_supabase.py
# Automated migration script to replace SQLite with Supabase in app.py

import re

def migrate_app_py():
    """Migrate app.py from SQLite to Supabase"""
    
    print("🔄 Starting migration from SQLite to Supabase...")
    
    # Read original file
    try:
        with open('app.py', 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        print("❌ Error: app.py not found!")
        return False
    
    # Create backup
    with open('app.py.backup', 'w', encoding='utf-8') as f:
        f.write(content)
    print("✅ Backup created: app.py.backup")
    
    # Step 1: Replace import
    print("\n📝 Step 1: Replacing imports...")
    content = content.replace('import sqlite3', 'from supabase_client import db\n# import sqlite3  # Migrated to Supabase')
    
    # Step 2: Replace get_db_connection function
    print("📝 Step 2: Updating get_db_connection()...")
    old_func = r'def get_db_connection\(\):\s*conn = sqlite3\.connect\(.*?\)\s*conn\.row_factory = .*?\s*return conn'
    new_func = '''def get_db_connection():
    """Return the Supabase client"""
    return db'''
    content = re.sub(old_func, new_func, content, flags=re.DOTALL)
    
    # Step 3: Replace cursor execution patterns
    print("📝 Step 3: Replacing cursor patterns...")
    
    # Pattern: cursor.execute("SELECT * FROM user WHERE email = ?"
    content = re.sub(
        r'cursor\.execute\(\s*"SELECT \* FROM user WHERE email = \?"\s*,\s*\(([^)]+)\)\s*\)\s*user = cursor\.fetchone\(\)',
        r'user = db.get_user_by_email(\1)',
        content
    )
    
    # Pattern: cursor.execute("SELECT * FROM user WHERE userid = ?"
    content = re.sub(
        r'cursor\.execute\(\s*"SELECT \* FROM user WHERE userid = \?"\s*,\s*\(([^)]+)\)\s*\)\s*user = cursor\.fetchone\(\)',
        r'user = db.get_user_by_id(\1)',
        content
    )
    
    # Pattern: SELECT * FROM ticket WHERE ticketid = ?
    content = re.sub(
        r'cursor\.execute\(\s*"SELECT \* FROM ticket WHERE ticketid = \?"\s*,\s*\(([^)]+)\)\s*\)\s*ticket = cursor\.fetchone\(\)',
        r'ticket = db.get_ticket_by_id(\1)',
        content
    )
    
    # Step 4: Replace INSERT patterns
    print("📝 Step 4: Replacing INSERT statements...")
    
    # Generic INSERT pattern - needs manual review
    insert_pattern = r'cursor\.execute\(\s*"(INSERT INTO \w+[^"]+)"\s*,\s*\(([^)]+)\)\s*\)'
    matches = re.finditer(insert_pattern, content)
    
    print(f"\n⚠️  Found {len(list(re.finditer(insert_pattern, content)))} INSERT statements to review manually")
    
    # Step 5: Remove conn.commit() and conn.close()
    print("📝 Step 5: Removing commit() and close() calls...")
    content = re.sub(r'\.commit\(\)', '# Removed: commit() - Supabase auto-commits', content)
    content = re.sub(r'conn\.close\(\)', '# Removed: close() - Not needed with Supabase', content)
    
    # Step 6: Replace cursor.fetchall() for common queries
    print("📝 Step 6: Replacing fetchall() patterns...")
    
    # SELECT * FROM user
    content = re.sub(
        r'cursor\.execute\(\s*"SELECT \* FROM user ORDER BY[^"]*"\s*\)\s*users = cursor\.fetchall\(\)',
        r'users = db.get_all_users()',
        content
    )
    
    # SELECT * FROM ticket
    content = re.sub(
        r'cursor\.execute\(\s*"SELECT \* FROM ticket ORDER BY[^"]*"\s*\)\s*tickets = cursor\.fetchall\(\)',
        r'tickets = db.get_all_tickets()',
        content
    )
    
    # Write migrated file
    print("\n💾 Writing migrated file...")
    with open('app.py.migrated', 'w', encoding='utf-8') as f:
        f.write(content)
    
    print("\n✅ Migration complete!")
    print("\n📁 Files created:")
    print("   - app.py.backup (original)")
    print("   - app.py.migrated (migrated version)")
    
    print("\n⚠️  IMPORTANT: Manual Review Required!")
    print("\nNext steps:")
    print("1. Compare app.py and app.py.migrated")
    print("2. Review INSERT statements (marked with comments)")
    print("3. Test thoroughly before deploying")
    print("4. If satisfied, rename: Copy-Item app.py.migrated app.py")
    
    return True

if __name__ == '__main__':
    migrate_app_py()
