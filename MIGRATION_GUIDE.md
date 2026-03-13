# 🔄 Complete Code Migration: SQLite → Supabase

## Step-by-Step Instructions for app.py

---

## ⚠️ **IMPORTANT: Backup First!**

Before making any changes:

```bash
# Create backup of your current app.py
Copy-Item app.py app.py.backup
```

---

## 📝 **Overview of Changes**

You need to replace **3 types of operations**:

1. **Database Connection** - Remove `sqlite3.connect()`
2. **SELECT Queries** - Use `db.get_*()` methods
3. **INSERT/UPDATE Queries** - Use `db.create_*()` / `db.update_*()` methods

---

## 🔧 **Step-by-Step Replacement Guide**

### **Change #1: Import supabase_client (Line 11)**

#### ❌ REMOVE:
```python
import sqlite3
```

#### ✅ ADD:
```python
from supabase_client import db
```

---

### **Change #2: Replace get_db_connection() Function**

Find this function (around line 60-70):

#### ❌ REMOVE:
```python
def get_db_connection():
    conn = sqlite3.connect('unihelp.db')
    conn.row_factory = sqlite3.Row
    return conn
```

#### ✅ REPLACE WITH:
```python
def get_db_connection():
    """Return the Supabase client"""
    return db
```

---

### **Change #3: Login Function (Around Line 200-250)**

Find the login route and look for user queries.

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM user WHERE email = ? AND passwordhash = ?", (email, password_hash))
user = cursor.fetchone()
conn.close()
```

#### ✅ NEW CODE:
```python
user = db.get_user_by_email(email)
if user and check_password_hash(user['passwordhash'], password):
    # Login successful
    pass
```

---

### **Change #4: Create User in Registration (Around Line 300-350)**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO user (name, email, passwordhash, role) 
    VALUES (?, ?, ?, ?)
""", (name, email, password_hash, role))
conn.commit()
userid = cursor.lastrowid
conn.close()
```

#### ✅ NEW CODE:
```python
new_user = db.create_user({
    'name': name,
    'email': email,
    'passwordhash': password_hash,
    'role': role,
    'isapproved': True  # or False if admin approval needed
})
userid = new_user['userid']
```

---

### **Change #5: Get All Users (Admin Panel)**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM user ORDER BY created_at DESC")
users = cursor.fetchall()
conn.close()
```

#### ✅ NEW CODE:
```python
users = db.get_all_users()
```

---

### **Change #6: Create Ticket (Around Line 500-550)**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO ticket (title, description, category, priority, userid) 
    VALUES (?, ?, ?, ?, ?)
""", (title, description, category, priority, session['user_id']))
conn.commit()
ticketid = cursor.lastrowid
conn.close()
```

#### ✅ NEW CODE:
```python
new_ticket = db.create_ticket({
    'title': title,
    'description': description,
    'category': category,
    'priority': priority,
    'userid': session['user_id']
})
ticketid = new_ticket['ticketid']
```

---

### **Change #7: Get All Tickets**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT t.*, u.name as creator_name 
    FROM ticket t
    JOIN user u ON t.userid = u.userid
    ORDER BY t.createdat DESC
""")
tickets = cursor.fetchall()
conn.close()
```

#### ✅ NEW CODE:
```python
tickets = db.get_all_tickets()
```

---

### **Change #8: Get Ticket by ID**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("SELECT * FROM ticket WHERE ticketid = ?", (ticket_id,))
ticket = cursor.fetchone()
conn.close()
```

#### ✅ NEW CODE:
```python
ticket = db.get_ticket_by_id(ticket_id)
```

---

### **Change #9: Update Ticket Status**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    UPDATE ticket 
    SET status = ?, assignedto = ? 
    WHERE ticketid = ?
""", (status, assigned_to, ticket_id))
conn.commit()
conn.close()
```

#### ✅ NEW CODE:
```python
db.update_ticket(ticket_id, {
    'status': status,
    'assignedto': assigned_to
})
```

---

### **Change #10: Get Comments**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT c.*, u.name as author_name 
    FROM comment c
    JOIN user u ON c.userid = u.userid
    WHERE c.ticketid = ?
    ORDER BY c.createdat ASC
""", (ticket_id,))
comments = cursor.fetchall()
conn.close()
```

#### ✅ NEW CODE:
```python
comments = db.get_comments_by_ticket(ticket_id)
```

---

### **Change #11: Create Comment**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    INSERT INTO comment (content, ticketid, userid) 
    VALUES (?, ?, ?)
""", (content, ticket_id, user_id))
conn.commit()
conn.close()
```

#### ✅ NEW CODE:
```python
db.create_comment({
    'content': content,
    'ticketid': ticket_id,
    'userid': user_id
})
```

---

### **Change #12: Get Tickets by User**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT * FROM ticket 
    WHERE userid = ? 
    ORDER BY createdat DESC
""", (user_id,))
tickets = cursor.fetchall()
conn.close()
```

#### ✅ NEW CODE:
```python
tickets = db.get_tickets_by_user(user_id)
```

---

### **Change #13: Get Tickets by Technician**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    SELECT * FROM ticket 
    WHERE assignedto = ? 
    ORDER BY createdat DESC
""", (technician_id,))
tickets = cursor.fetchall()
conn.close()
```

#### ✅ NEW CODE:
```python
tickets = db.get_tickets_by_technician(technician_id)
```

---

### **Change #14: Update User (Profile)**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()
cursor.execute("""
    UPDATE user 
    SET name = ?, email = ? 
    WHERE userid = ?
""", (name, email, user_id))
conn.commit()
conn.close()
```

#### ✅ NEW CODE:
```python
db.update_user(user_id, {
    'name': name,
    'email': email
})
```

---

### **Change #15: Dashboard Statistics**

#### ❌ OLD CODE:
```python
conn = get_db_connection()
cursor = conn.cursor()

# Count tickets
cursor.execute("SELECT COUNT(*) FROM ticket")
total_tickets = cursor.fetchone()[0]

# Count users by role
cursor.execute("SELECT role, COUNT(*) FROM user GROUP BY role")
users_by_role = cursor.fetchall()

conn.close()
```

#### ✅ NEW CODE:
```python
# Get user count by role
users_by_role = db.get_user_count_by_role()

# For ticket stats, you might need to query directly
all_tickets = db.get_all_tickets()
total_tickets = len(all_tickets)
```

---

## 🎯 **Quick Reference Table**

| Operation | Old (SQLite) | New (Supabase) |
|-----------|--------------|----------------|
| **Connect** | `sqlite3.connect('unihelp.db')` | `db.client` |
| **SELECT one** | `cursor.execute("SELECT...WHERE id=?")` | `db.get_*_by_id(id)` |
| **SELECT many** | `cursor.execute("SELECT...")` | `db.get_all_*()` |
| **INSERT** | `cursor.execute("INSERT...")` | `db.create_*(data)` |
| **UPDATE** | `cursor.execute("UPDATE...")` | `db.update_*(id, data)` |
| **DELETE** | `cursor.execute("DELETE...")` | `db.client.table().delete()` |
| **Commit** | `conn.commit()` | Automatic |
| **Close** | `conn.close()` | Not needed |

---

## 🧪 **Testing Checklist**

After making changes, test these features:

- [ ] Login/Logout
- [ ] User Registration
- [ ] Admin Dashboard
- [ ] Create Ticket
- [ ] View Tickets
- [ ] Assign Ticket to Technician
- [ ] Add Comments
- [ ] Update Profile
- [ ] View Statistics

---

## 🆘 **Common Issues & Solutions**

### **Issue 1: "db is not defined"**
**Solution:** Make sure you imported it at the top:
```python
from supabase_client import db
```

### **Issue 2: "NoneType has no attribute 'select'"**
**Solution:** Check if Supabase connected properly. Run `python test_supabase.py`

### **Issue 3: Data not showing up**
**Solution:** Check if you have data in Supabase. Open Table Editor and verify.

### **Issue 4: Foreign key errors**
**Solution:** Make sure referenced IDs exist (e.g., valid userid before creating ticket)

---

## 💡 **Pro Tips**

1. **Make changes incrementally** - Don't change everything at once
2. **Test after each change** - Fix issues immediately
3. **Keep backup handy** - You can always revert
4. **Use print statements** - Debug with `print(f"User: {user}")`
5. **Check Supabase logs** - Go to Logs tab in Supabase dashboard

---

## ✅ **Final Verification**

Run your app:
```bash
python app.py
```

Visit http://localhost:5000 and test all features!

---

## 🚀 **Next Steps After Local Testing**

Once everything works locally:

1. Commit changes to Git
2. Push to GitHub
3. Add Supabase env vars to Vercel
4. Deploy to production

---

**Ready to start? Begin with Change #1 and work through them systematically!** 

Need help with a specific change? Let me know which function you're working on! 😊
