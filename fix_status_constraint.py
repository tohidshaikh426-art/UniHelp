import sqlite3

def fix_status_constraint():
    """Fix the status column constraint to include all required status values"""

    conn = sqlite3.connect('unihelp.db')
    cursor = conn.cursor()

    print("🔧 Fixing status constraint...")

    # SQLite doesn't support ALTER TABLE to modify CHECK constraints
    # We need to recreate the table with the correct constraint

    # First, backup the existing data
    cursor.execute('SELECT * FROM ticket')
    tickets = cursor.fetchall()

    # Get column names
    cursor.execute('PRAGMA table_info(ticket)')
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]

    # Drop the old table
    cursor.execute('DROP TABLE ticket')

    # Create the new table with correct status constraint
    cursor.execute('''CREATE TABLE ticket (
        ticketid INTEGER PRIMARY KEY AUTOINCREMENT,
        title VARCHAR(200) NOT NULL,
        description TEXT NOT NULL,
        category VARCHAR(50) NOT NULL,
        status VARCHAR(30) DEFAULT 'Open' CHECK(status IN ('Open', 'In Progress', 'Pending', 'Resolved', 'Closed', 'Reopened')),
        filepath VARCHAR(255),
        createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updatedat TIMESTAMP,
        userid INTEGER NOT NULL,
        assignedto INTEGER,
        resolvedat TIMESTAMP,
        resolvedby INTEGER,
        time_spent_hours REAL DEFAULT 0,
        resolution_notes TEXT,
        satisfaction_rating INTEGER CHECK(satisfaction_rating >= 1 AND satisfaction_rating <= 5),
        priority VARCHAR(20) DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent')),
        FOREIGN KEY (userid) REFERENCES user(userid) ON DELETE CASCADE,
        FOREIGN KEY (assignedto) REFERENCES user(userid) ON DELETE SET NULL,
        FOREIGN KEY (resolvedby) REFERENCES user(userid) ON DELETE SET NULL
    )''')

    # Insert the data back
    placeholders = ', '.join(['?' for _ in column_names])
    columns_str = ', '.join(column_names)

    for ticket in tickets:
        try:
            cursor.execute(f'INSERT INTO ticket ({columns_str}) VALUES ({placeholders})', ticket)
        except sqlite3.IntegrityError as e:
            print(f"Warning: Could not insert ticket {ticket[0]}: {e}")
            # Try to fix status if it's invalid
            ticket_list = list(ticket)
            if ticket_list[column_names.index('status')] not in ['Open', 'In Progress', 'Pending', 'Resolved', 'Closed', 'Reopened']:
                ticket_list[column_names.index('status')] = 'Open'
                cursor.execute(f'INSERT INTO ticket ({columns_str}) VALUES ({placeholders})', ticket_list)

    conn.commit()
    conn.close()

    print("✅ Status constraint fixed!")

if __name__ == '__main__':
    fix_status_constraint()