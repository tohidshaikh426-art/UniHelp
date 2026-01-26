import sqlite3

conn = sqlite3.connect('unihelp.db')
cursor = conn.cursor()

# Get the CREATE TABLE statement
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='ticket'")
result = cursor.fetchone()
print('Ticket table schema:')
print(result[0])

conn.close()