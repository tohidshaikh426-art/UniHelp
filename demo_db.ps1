# SQLite Database Demo Commands
# For Final Year Project Presentation

echo "========================================"
echo "📊 UniHelp Database Demo"
echo "========================================"
echo ""

echo "1️⃣  Showing all database tables..."
sqlite3 unihelp.db ".tables"
echo ""

echo "2️⃣  User table structure..."
sqlite3 unihelp.db ".schema user" | Select-String -Pattern "CREATE TABLE" -Context 0,10
echo ""

echo "3️⃣  All users in the system..."
sqlite3 -header -column unihelp.db "SELECT userid, name, email, role FROM user;"
echo ""

echo "4️⃣  Ticket statistics..."
sqlite3 -header -column unihelp.db "SELECT status, COUNT(*) as count FROM ticket GROUP BY status;"
echo ""

echo "5️⃣  Recent tickets with creator info..."
sqlite3 -header -column unihelp.db @"
SELECT 
    t.ticketid,
    t.title,
    u.name as creator,
    t.status,
    t.createdat
FROM ticket t
JOIN user u ON t.userid = u.userid
ORDER BY t.createdat DESC
LIMIT 5;
"@
echo ""

echo "6️⃣  Record counts for all tables..."
sqlite3 unihelp.db @"
SELECT 'user' as table_name, COUNT(*) as count FROM user
UNION ALL
SELECT 'ticket', COUNT(*) FROM ticket
UNION ALL
SELECT 'comment', COUNT(*) FROM comment
UNION ALL
SELECT 'chat_session', COUNT(*) FROM chat_session
UNION ALL
SELECT 'ticket_history', COUNT(*) FROM ticket_history;
"@
echo ""

echo "✅ Database demo complete!"
