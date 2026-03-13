# list_tables.py
# Quick CLI tool to show database tables and data

import sqlite3
import os

def connect_db():
    """Connect to the database"""
    # Find database file
    possible_paths = ['unihelp.db', '../unihelp.db']
    
    for path in possible_paths:
        if os.path.exists(path):
            return sqlite3.connect(path), path
    
    print("❌ Database not found!")
    return None, None

def show_tables(cursor):
    """Show all tables in the database"""
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n" + "="*60)
    print("📊 DATABASE TABLES")
    print("="*60)
    print(f"\nFound {len(tables)} tables:\n")
    
    for i, table in enumerate(tables, 1):
        table_name = table[0]
        if not table_name.startswith('sqlite_'):
            print(f"  {i}. {table_name}")
    
    print("\n" + "="*60)

def show_table_schema(cursor, table_name):
    """Show schema/structure of a specific table"""
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()
    
    print(f"\n📋 Table: {table_name}")
    print("-"*60)
    print(f"{'Column':<20} {'Type':<15} {'NotNull':<8} {'Default':<15}")
    print("-"*60)
    
    for col in columns:
        cid, name, dtype, notnull, default, pk = col
        pk_marker = " 🔑 PK" if pk else ""
        print(f"{name:<20} {dtype:<15} {bool(notnull)!s:<8} {str(default):<15}{pk_marker}")
    
    print("-"*60)

def show_table_data(cursor, table_name, limit=5):
    """Show sample data from a table"""
    try:
        cursor.execute(f"SELECT * FROM {table_name} LIMIT {limit}")
        rows = cursor.fetchall()
        
        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [col[1] for col in cursor.fetchall()]
        
        print(f"\n📄 Table: {table_name} (Showing {len(rows)} rows)")
        print("-"*60)
        
        # Print headers
        header = " | ".join([f"{col:<15}" for col in columns])
        print(header)
        print("-"*60)
        
        # Print rows
        for row in rows:
            row_str = " | ".join([f"{str(val):<15}" for val in row])
            print(row_str)
        
        print("-"*60)
        
    except Exception as e:
        print(f"Error: {e}")

def main():
    """Main function"""
    conn, db_path = connect_db()
    
    if not conn:
        return
    
    print(f"\n✅ Connected to: {db_path}")
    
    cursor = conn.cursor()
    
    # Show all tables
    show_tables(cursor)
    
    # Show schema for key tables
    key_tables = ['user', 'ticket', 'chat_session', 'ticket_history']
    
    for table in key_tables:
        try:
            show_table_schema(cursor, table)
        except:
            pass
    
    # Show sample data
    print("\n\n📊 SAMPLE DATA")
    print("="*60)
    
    # Users
    show_table_data(cursor, 'user', 5)
    
    # Tickets
    show_table_data(cursor, 'ticket', 3)
    
    # Count records in each table
    print("\n\n📈 RECORD COUNTS")
    print("="*60)
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%'")
    tables = cursor.fetchall()
    
    for table in tables:
        table_name = table[0]
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"  {table_name:<30} : {count} records")
    
    print("="*60)
    
    conn.close()
    print("\n✅ Done!\n")

if __name__ == '__main__':
    main()
