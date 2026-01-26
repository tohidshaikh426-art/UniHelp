import sqlite3

conn = sqlite3.connect('unihelp.db')
cursor = conn.cursor()

# Check what tables exist
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
print('Tables in database:')
for table in tables:
    print('-', table[0])

# Check if new tables exist
new_tables = ['technician_work_log', 'ticket_history', 'monthly_reports_cache']
print('\nChecking for new tables:')
for table in new_tables:
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f'✓ {table}: {count} records')
    except sqlite3.OperationalError as e:
        print(f'✗ {table}: Table does not exist - {e}')

conn.close()