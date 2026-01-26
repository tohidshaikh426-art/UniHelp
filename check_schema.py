import sqlite3

conn = sqlite3.connect('unihelp.db')
cursor = conn.cursor()

# Check ticket table schema
cursor.execute('PRAGMA table_info(ticket)')
columns = cursor.fetchall()
print('Ticket table columns:')
for col in columns:
    print(f'  {col[1]} - {col[2]}')

conn.close()