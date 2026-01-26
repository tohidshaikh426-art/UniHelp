import sqlite3

def migrate_ticket_table():
    """Add missing columns to the ticket table"""

    conn = sqlite3.connect('unihelp.db')
    cursor = conn.cursor()

    print("🔧 Migrating ticket table...")

    # Check current columns
    cursor.execute('PRAGMA table_info(ticket)')
    existing_columns = [col[1] for col in cursor.fetchall()]

    # Columns to add
    columns_to_add = [
        ('priority', "VARCHAR(20) DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent'))"),
        ('updatedat', 'TIMESTAMP DEFAULT CURRENT_TIMESTAMP'),
        ('resolvedat', 'TIMESTAMP'),
        ('resolvedby', 'INTEGER'),
        ('time_spent_hours', 'REAL DEFAULT 0'),
        ('resolution_notes', 'TEXT'),
        ('satisfaction_rating', 'INTEGER CHECK(satisfaction_rating >= 1 AND satisfaction_rating <= 5)')
    ]

    for col_name, col_def in columns_to_add:
        if col_name not in existing_columns:
            try:
                cursor.execute(f'ALTER TABLE ticket ADD COLUMN {col_name} {col_def}')
                print(f"✓ Added column: {col_name}")
            except sqlite3.OperationalError as e:
                print(f"✗ Failed to add {col_name}: {e}")
        else:
            print(f"✓ Column {col_name} already exists")

    # Add foreign key constraints if they don't exist
    try:
        cursor.execute('PRAGMA foreign_key_list(ticket)')
        fk_list = cursor.fetchall()
        fk_names = [fk[3] for fk in fk_list]  # fk[3] is the column name

        if 'resolvedby' not in fk_names:
            # Note: SQLite doesn't support adding foreign keys to existing tables
            # We'll handle this in the application logic instead
            print("⚠ Foreign key constraints will be handled in application logic")
    except:
        pass

    conn.commit()
    conn.close()

    print("✅ Migration completed!")

if __name__ == '__main__':
    migrate_ticket_table()