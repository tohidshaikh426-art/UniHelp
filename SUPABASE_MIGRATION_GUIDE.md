# 🚀 Vercel + Supabase Migration Guide

## Complete Step-by-Step Instructions

---

## ⏱️ **Time Estimate:** 2-3 hours total

---

## 📋 **Phase 1: Setup Supabase (30 minutes)**

### **Step 1: Create Supabase Account**

1. Go to https://supabase.com
2. Click "Start your project" or "Sign In"
3. Sign in with GitHub (recommended) or email

### **Step 2: Create New Project**

1. Click **"New Project"**
2. Fill in:
   - **Name:** `UniHelp`
   - **Database Password:** Choose a strong password (SAVE THIS!)
   - **Region:** Select closest to you (e.g., East US, West Europe)
   - **Free Tier:** Perfect for your needs

3. Click **"Create new project"**
4. Wait 2-3 minutes for setup

### **Step 3: Get API Credentials**

1. Go to **Settings** (gear icon) → **API**
2. Copy these values:
   - **Project URL:** `https://xxxxx.supabase.co`
   - **anon/public key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
   - **service_role key:** `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...` (keep secret!)

⚠️ **Save these securely!**

---

## 🗄️ **Phase 2: Migrate Database Schema (45 minutes)**

### **Step 1: Open SQL Editor**

1. In Supabase dashboard, click **"SQL Editor"** (left sidebar)
2. Click **"New query"**

### **Step 2: Run Migration Script**

1. Open `supabase_migration.sql` file (I created this for you)
2. Copy ALL the content
3. Paste into Supabase SQL Editor
4. Click **"Run"** or press `Ctrl+Enter`

✅ You should see: "Success. No rows returned"

### **Step 3: Verify Tables**

1. Click **"Table Editor"** (left sidebar)
2. You should see all 11 tables:
   - user
   - ticket
   - comment
   - chat_session
   - chat_message
   - chatbot_interaction
   - user_presence
   - live_chat
   - technician_work_log
   - ticket_history
   - monthly_reports_cache

---

## 🔧 **Phase 3: Update Your Code (1 hour)**

### **Step 1: Install Supabase Client**

```bash
# Activate virtual environment
.\.venv\Scripts\Activate

# Install supabase
pip install supabase

# Add to requirements.txt
echo "supabase==2.3.4" >> requirements.txt
```

### **Step 2: Update .env File**

Create/edit `.env` file in your project root:

```bash
# Your existing Gemini key
GEMINI_API_KEY=AIzaSyAwqiN2F5Ri5l6R8rTtd-aDhAKb-vV1pus

# NEW: Supabase credentials
SUPABASE_URL=https://your-project-id.supabase.co
SUPABASE_KEY=your-anon-key-here

# Flask config
FLASK_ENV=development
SECRET_KEY=your-secret-key
```

⚠️ **Replace `your-project-id` and `your-anon-key` with actual values!**

### **Step 3: Replace Database Code in app.py**

This is the BIG change. You need to replace all SQLite code with Supabase calls.

#### **OLD CODE (SQLite):**
```python
import sqlite3

# Connect to database
conn = sqlite3.connect('unihelp.db')
cursor = conn.cursor()

# Query users
cursor.execute("SELECT * FROM user WHERE email = ?", (email,))
user = cursor.fetchone()

# Insert user
cursor.execute("INSERT INTO user (...) VALUES (...)", data)
conn.commit()

conn.close()
```

#### **NEW CODE (Supabase):**
```python
from supabase_client import db

# Query users
user = db.get_user_by_email(email)

# Insert user
new_user = db.create_user({
    'name': name,
    'email': email,
    'passwordhash': hashed_pw,
    'role': role
})
```

### **Step 4: Use the Supabase Client Module**

I've already created `supabase_client.py` for you! It has all the methods you need:

```python
from supabase_client import db

# User operations
user = db.get_user_by_email('admin@unihelp.com')
all_users = db.get_all_users()
db.create_user(user_data)
db.update_user(user_id, data)

# Ticket operations
tickets = db.get_all_tickets()
ticket = db.get_ticket_by_id(ticket_id)
db.create_ticket(ticket_data)
db.update_ticket(ticket_id, data)

# Comment operations
comments = db.get_comments_by_ticket(ticket_id)
db.create_comment(comment_data)
```

---

## 🔄 **Phase 4: Test Locally (30 minutes)**

### **Step 1: Test Connection**

```bash
python -c "from supabase_client import db; print('Connected!' if db.client else 'Failed')"
```

Should output: `Connected!`

### **Step 2: Test Basic Operations**

```bash
# Test user lookup
python -c "from supabase_client import db; print(db.get_user_by_email('admin@unihelp.com'))"
```

### **Step 3: Run Your App**

```bash
python app.py
```

Test:
- Login
- Create ticket
- View tickets
- Add comments

---

## 🚀 **Phase 5: Deploy to Vercel (15 minutes)**

### **Step 1: Update Vercel Environment Variables**

1. Go to https://vercel.com/dashboard
2. Select your UniHelp project
3. Go to **Settings** → **Environment Variables**
4. Add these:
   - `GEMINI_API_KEY`
   - `SUPABASE_URL`
   - `SUPABASE_KEY`
   - `SECRET_KEY`
   - `FLASK_ENV`

### **Step 2: Redeploy**

```bash
# Commit your changes
git add .
git commit -m "Migrate to Supabase PostgreSQL"
git push

# Vercel will auto-deploy
# Or manually trigger:
vercel --prod
```

---

## ✅ **Migration Checklist**

- [ ] Created Supabase account
- [ ] Created UniHelp project
- [ ] Saved database password
- [ ] Copied API keys
- [ ] Ran migration SQL script
- [ ] Verified all 11 tables exist
- [ ] Installed supabase Python package
- [ ] Updated requirements.txt
- [ ] Created .env with Supabase credentials
- [ ] Replaced SQLite code with Supabase client
- [ ] Tested locally
- [ ] Added environment variables to Vercel
- [ ] Deployed to Vercel
- [ ] Tested production deployment

---

## 🎯 **Code Changes Summary**

### **Files to Modify:**

1. **app.py** - Replace all `sqlite3.connect()` calls with `db` from `supabase_client`
2. **requirements.txt** - Add `supabase==2.3.4`
3. **.env** - Add Supabase credentials
4. **supabase_client.py** - Already created, just import it

### **Key Changes:**

| Operation | Old (SQLite) | New (Supabase) |
|-----------|--------------|----------------|
| Connect | `sqlite3.connect('unihelp.db')` | `db.client` |
| SELECT | `cursor.execute("SELECT...")` | `db.get_*()` |
| INSERT | `cursor.execute("INSERT...")` | `db.create_*()` |
| UPDATE | `cursor.execute("UPDATE...")` | `db.update_*()` |
| DELETE | `cursor.execute("DELETE...")` | `db.client.table().delete()` |

---

## 💡 **Pro Tips**

### **During Migration:**

1. **Keep SQLite as backup** - Don't delete it until Supabase works perfectly
2. **Test each function** - Login, create ticket, view tickets, etc.
3. **Use try-except blocks** - Handle connection errors gracefully
4. **Log errors** - Add print statements during development

### **For Presentation:**

You can tell examiners:
> "I migrated from SQLite to PostgreSQL via Supabase to demonstrate understanding of both database types and cloud deployment. The normalized schema remained the same, showing good database design principles."

---

## 🆘 **Troubleshooting**

### **Error: "Table does not exist"**
- Check if you ran the migration SQL script
- Verify table names in Supabase Table Editor

### **Error: "Connection failed"**
- Check SUPABASE_URL and SUPABASE_KEY in .env
- Make sure they match exactly (no extra spaces)

### **Error: "Module not found: supabase"**
- Run: `pip install supabase`
- Activate virtual environment first

### **Data not showing up**
- Check Supabase Table Editor to verify data exists
- Check browser console for errors
- Verify your queries are correct

---

## 📊 **Benefits of This Setup**

✅ **PostgreSQL Database** - Industry standard  
✅ **Real-time Capabilities** - Can add live features later  
✅ **Better Scalability** - Handles more concurrent users  
✅ **Professional Setup** - Shows advanced skills  
✅ **Still on Vercel** - Keeps serverless benefits  
✅ **Free Tier** - No cost for your project  

---

## 🎓 **What This Shows Examiners**

1. **Database Migration Skills** - Can move between databases
2. **Cloud Services Knowledge** - Using modern platforms
3. **Scalability Awareness** - Understanding growth considerations
4. **Professional Practices** - Using industry-standard tools
5. **Adaptability** - Learning new technologies quickly

---

## ⏭️ **Next Steps After Migration**

Once migrated, you can:
- Add real-time notifications
- Implement row-level security
- Use PostgreSQL-specific features
- Scale to thousands of users
- Add database backups
- Set up monitoring

---

**Ready to start? Begin with Phase 1 and take it step by step!** 🚀

Need help with any specific phase? Let me know! 😊
