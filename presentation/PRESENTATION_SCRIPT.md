# UniHelp Backend Presentation Script
## For Final Year Project Defense

---

## 🎤 **Opening Statement (30 seconds)**

"Good morning/afternoon. Today I'll present the backend architecture of UniHelp, an IT helpdesk management system I developed using Python Flask and SQLite database. The system features role-based access control, AI-powered chatbot integration, and comprehensive ticket lifecycle management."

---

## 📊 **Part 1: Database Overview (2 minutes)**

### **What to Say:**
"My backend uses SQLite database with 11 normalized tables designed to handle:
- User authentication with 4 role types (Admin, Technician, Staff, Student)
- Complete ticket management from creation to resolution
- Real-time chat functionality
- Work logging and analytics
- Full audit trail for compliance"

### **Actions:**
1. Open `DATABASE_SCHEMA.md` file
2. Show the ERD diagram
3. Point out key relationships

### **Key Points to Emphasize:**
✅ Proper foreign key constraints for data integrity  
✅ Timestamps on all records for tracking  
✅ Scalable design patterns  

---

## 🔐 **Part 2: Security Features (1 minute)**

### **What to Say:**
"Security was a priority in my design:
- Passwords are hashed using Werkzeug's bcrypt implementation
- Role-based access control ensures users only see authorized data
- Session management prevents unauthorized access
- Input validation prevents SQL injection attacks"

### **Show Code:**
Open `app.py` lines 9-10:
```python
from werkzeug.security import generate_password_hash, check_password_hash
```

And show password hashing in `db_init.py` line 112:
```python
admin_password = generate_password_hash('admin123')
```

---

## 🎯 **Part 3: Core Functionality Demo (3 minutes)**

### **A. Ticket Creation Flow**

**Say:** "Let me show how a ticket flows through the system..."

**Show:** Run these SQL queries in sequence:

```sql
-- 1. Create a sample ticket
INSERT INTO ticket (title, description, category, priority, userid)
VALUES ('WiFi not working', 'Cannot connect to campus WiFi', 'Network', 'High', 4);

-- 2. View the ticket
SELECT * FROM ticket WHERE ticketid = LAST_INSERT_ROWID();

-- 3. Assign to technician
UPDATE ticket SET assignedto = 2, status = 'In Progress' WHERE ticketid = LAST_INSERT_ROWID();

-- 4. Track the change
INSERT INTO ticket_history (ticketid, changed_by, old_status, new_status, change_reason)
VALUES (LAST_INSERT_ROWID(), 1, 'Open', 'In Progress', 'Assigned to network team');
```

**Emphasize:** "Every state change is logged in ticket_history for complete audit trail."

---

### **B. Role-Based Permissions**

**Say:** "Different users have different capabilities..."

**Show Query:**
```sql
-- Show all users and their roles
SELECT name, email, role, isapproved, created_at 
FROM user 
ORDER BY role, created_at;
```

**Explain:**
- Admin: Can view/edit everything
- Technician: Can update tickets, log work hours
- Staff/Student: Can only create and view own tickets

---

### **C. Analytics & Reporting**

**Say:** "The system provides comprehensive analytics..."

**Show Query:**
```sql
-- Monthly ticket statistics
SELECT 
    strftime('%Y-%m', createdat) as month,
    COUNT(*) as total_tickets,
    SUM(CASE WHEN status = 'Resolved' THEN 1 ELSE 0 END) as resolved,
    AVG(JULIANDAY(resolvedat) - JULIANDAY(createdat)) as avg_resolution_days
FROM ticket
GROUP BY strftime('%Y-%m', createdat)
ORDER BY month DESC;
```

**Explain:** "This query powers the monthly reports that admins can view in the dashboard."

---

## 🤖 **Part 4: AI Integration (1 minute)**

### **What to Say:**
"I've integrated Google's Gemini AI for initial support:
- Chatbot handles common queries automatically
- Unresolved issues escalate to human technicians
- All interactions are logged for training purposes"

### **Show Tables:**
Point to `chat_session`, `chat_message`, and `chatbot_interaction` tables in schema

### **Show Code:**
Open `app.py` lines 29-38:
```python
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-1.5-pro')
    AI_ENABLED = True
```

---

## 📈 **Part 5: Performance Optimization (1 minute)**

### **What to Say:**
"To ensure good performance:
- I use indexed primary keys for fast lookups
- Monthly reports are pre-computed and cached
- File uploads are limited to 16MB
- Database connections are properly closed after use"

### **Show:**
Point to `monthly_reports_cache` table:
"This table stores pre-aggregated data so complex reports load instantly instead of querying millions of rows every time."

---

## 🚀 **Part 6: Deployment Strategy (1 minute)**

### **What to Say:**
"The application is deployed on Vercel's serverless platform:
- Flask app runs as serverless functions
- SQLite works perfectly in serverless environment
- No external database server needed
- Environment variables manage configuration"

### **Show Files:**
- `Procfile` - deployment configuration
- `runtime.txt` - Python version specification
- `.env` - environment variables (without showing API key)

---

## 💻 **Live Demo Options (Choose One)**

### **Option A: Database Browser Demo**
1. Open DB Browser for SQLite
2. Load `unihelp.db`
3. Browse each table
4. Execute a complex query

### **Option B: Running Application Demo**
```bash
# Start the app
python app.py

# Navigate to: http://localhost:5000
# Login as admin
# Show admin dashboard with statistics
```

### **Option C: API Endpoint Demo**
```bash
# Test ticket creation endpoint
curl -X POST http://localhost:5000/ticket/create \
  -d "title=Test&description=Demo"
```

---

## ❓ **Anticipated Questions & Answers**

### **Q: Why SQLite instead of MySQL/PostgreSQL?**
**A:** "SQLite is perfect for this scale because:
- No server setup required
- Works seamlessly with Vercel serverless
- Handles thousands of transactions per day easily
- Can migrate to PostgreSQL later with minimal code changes
- Ideal for development and prototyping"

### **Q: How do you handle concurrent users?**
**A:** "SQLite supports multiple readers and one writer at a time. For higher concurrency:
- Transactions are kept short
- Proper error handling for locked database
- Can upgrade to PostgreSQL without changing business logic"

### **Q: What about database backups?**
**A:** "Since it's a single file, backup is simple:
- Copy `unihelp.db` to cloud storage
- Automated daily backups via cron job
- Version control for schema changes via `db_init.py`"

### **Q: How scalable is this design?**
**A:** "Very scalable because:
- Normalized design prevents data redundancy
- Foreign keys maintain integrity
- Business logic is in Flask, not stored procedures
- Can horizontally scale by migrating to PostgreSQL"

---

## 🎯 **Closing Statement (30 seconds)**

"In conclusion, UniHelp's backend demonstrates:
- Professional database design with proper normalization
- Secure authentication and authorization
- Complete audit trails for accountability
- AI integration for modern support automation
- Production-ready deployment on serverless infrastructure

This system could handle real-world IT support operations and can scale as needed. Thank you. I'm happy to answer any questions."

---

## 📋 **Checklist Before Presentation**

- [ ] Install DB Browser for SQLite
- [ ] Test all demo queries work
- [ ] Have backup screenshots ready
- [ ] Print DATABASE_SCHEMA.md for reference
- [ ] Test the running application
- [ ] Prepare answers for Q&A
- [ ] Have internet backup if live demo fails

---

## 🛠️ **Technical Setup Commands**

### **Before Presentation:**
```bash
# Ensure database is initialized
python db_init.py

# Check database health
python check_db.py

# Start application
python app.py
```

### **If Something Goes Wrong:**
```bash
# Reset database
Remove-Item unihelp.db
python db_init.py
```

---

**Good luck with your presentation! 🎓✨**
