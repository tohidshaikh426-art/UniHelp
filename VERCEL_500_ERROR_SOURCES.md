# 🚨 CRITICAL: 500 Internal Server Error Sources on Vercel

## ⚠️ PROBLEM SUMMARY

Your app has **12 functions still using SQLite** (`get_db_connection()`) which will **FAIL on Vercel** because:
- ❌ SQLite needs local file access (not available on Vercel serverless)
- ✅ Supabase is your production database (works on Vercel)

---

## 📍 ALL SQLITE USAGES CAUSING 500 ERRORS

### **Priority 1: Critical User-Facing Features** 🔴

#### 1. `escalate_to_ticket()` - Line 1287
**Route**: `/api/chat/escalate`  
**Impact**: HIGH - Users can't create tickets from chat  
**Error**: "unable to open database file"

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
chat_session = conn.execute('SELECT * FROM chat_session WHERE sessionid = ?...', (session_id, ...))
```

**Fix Needed**: Use `db.get_chat_session_by_id()` and `db.create_ticket()`

---

#### 2. `get_chat_history()` - Line 1345
**Route**: `/api/chat/history/<session_id>`  
**Impact**: HIGH - Can't view past chat sessions  
**Error**: "no such table: chat_session"

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
messages = conn.execute('SELECT * FROM chat_message WHERE sessionid = ?', (session_id,))
```

**Fix Needed**: Use `db.get_chat_messages_by_session()`

---

#### 3. `admin_send_direct_message()` - Line 1387
**Route**: `/admin/send_direct_message`  
**Impact**: MEDIUM - Admin can't message technicians  
**Error**: "unable to open database file"

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
tech = conn.execute('SELECT * FROM user WHERE userid = ?', (technician_id,))
```

**Fix Needed**: Use `db.get_user_by_id()`

---

### **Priority 2: Admin Reporting Features** 🟠

#### 4. `monthly_report()` - Line 1471
**Route**: `/admin/reports/monthly/<year>/<month>`  
**Impact**: MEDIUM - Admin reports broken  
**Error**: Multiple SQL queries will fail

**SQLite Queries** (ALL WILL FAIL):
- Line 1487: Ticket statistics
- Line 1501: Category statistics  
- Line 1513: Technician performance
- Line 1532: Work log hours
- Line 1549: Daily trend

**Fix Needed**: Rewrite using Supabase client queries or use Python for calculations

---

#### 5. `custom_date_report()` - Line 1592
**Route**: `/admin/reports/custom`  
**Impact**: MEDIUM - Custom date reports broken  
**Similar Issues**: Same as monthly_report

---

### **Priority 3: Technician Work Logging** 🟡

#### 6. `start_work_session()` - Line 1700
**Route**: `/api/work/start`  
**Impact**: MEDIUM - Technicians can't log work time  
**Error**: "unable to open database file"

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
active_session = conn.execute('SELECT * FROM technician_work_log WHERE technicianid = ?', (tech_id,))
cursor = conn.execute('INSERT INTO technician_work_log...')
worklog_id = cursor.lastrowid
```

**Fix Needed**: Use `db.client.table('technician_work_log').insert()`

---

#### 7. `end_work_session()` - Line 1733
**Route**: `/api/work/end/<worklog_id>`  
**Impact**: MEDIUM - Can't end work sessions  
**Error**: Update query will fail

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
work_session = conn.execute('SELECT * FROM technician_work_log WHERE worklogid = ?', (worklog_id,))
conn.execute('UPDATE technician_work_log SET end_time..., hours_worked...')
```

**Fix Needed**: Use Supabase select + update

---

#### 8. `get_active_work_session()` - Line 1779
**Route**: `/api/work/active`  
**Impact**: LOW - Status check fails silently  
**Error**: Select query fails

**Fix Needed**: Use `db.client.table('technician_work_log').select()`

---

### **Priority 4: Presence & Utility Functions** 🟢

#### 9. `update_presence()` - Line 1855
**Route**: `/api/presence/update`  
**Impact**: HIGH - Online status not updating  
**Error**: INSERT fails

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
conn.execute('INSERT OR REPLACE INTO user_presence (userid, status, last_seen) VALUES (?, ?, ?)')
```

**Fix Needed**: Use Supabase upsert or insert+handle conflict

---

#### 10. `get_online_technicians()` - Line 1872
**Route**: `/api/presence/technicians`  
**Impact**: MEDIUM - Can't see online technicians  
**Error**: JOIN query fails

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
technicians = conn.execute('''
    SELECT u.userid, u.name, u.email, p.status, p.last_seen
    FROM user u
    JOIN user_presence p ON u.userid = p.userid
    WHERE ...
''')
```

**Fix Needed**: Fetch separately and join in Python

---

#### 11. `get_conversation_context()` - Line 2480
**Function**: Helper for AI chatbot  
**Impact**: HIGH - AI chat loses context  
**Error**: Select query fails

```python
# ❌ BROKEN ON VERCEL
conn = get_db_connection()
messages = conn.execute('SELECT sender, message FROM chat_message WHERE sessionid = ?', (session_id,))
```

**Fix Needed**: Use `db.get_chat_messages_by_session()`

---

### **Already Fixed** ✅

These were using SQLite but have been migrated to Supabase:
- ✅ `end_live_chat()` - Fixed (was line 1894)
- ✅ `technician_send_message()` - Fixed (was line 1975)
- ✅ `request_live_technician()` - Fixed (was line 1204)

---

## 🎯 ERROR PATTERNS YOU'LL SEE ON VERCEL

### Pattern 1: "unable to open database file"
```
Error: unable to open database file
  File "app.py", line XXXX, in <function>
    conn = get_db_connection()
```

**Cause**: Vercel serverless can't access local SQLite file

---

### Pattern 2: "no such table: <table_name>"
```
sqlite3.OperationalError: no such table: chat_message
  File "app.py", line XXXX, in <function>
    messages = conn.execute('SELECT * FROM chat_message...')
```

**Cause**: Even if SQLite worked, tables don't exist on Vercel

---

### Pattern 3: "database is locked"
```
sqlite3.OperationalError: database is locked
  File "app.py", line XXXX, in <function>
    conn.execute('UPDATE...')
```

**Cause**: Concurrent requests lock SQLite (Vercel is multi-user)

---

## 📊 IMPACT ASSESSMENT

| Feature | Status | Priority | Users Affected |
|---------|--------|----------|----------------|
| Chat → Ticket Escalation | ❌ Broken | HIGH | All users |
| Chat History View | ❌ Broken | HIGH | All users |
| Admin Direct Messaging | ❌ Broken | MEDIUM | Admins |
| Monthly Reports | ❌ Broken | MEDIUM | Admins |
| Custom Date Reports | ❌ Broken | MEDIUM | Admins |
| Work Session Start | ❌ Broken | MEDIUM | Technicians |
| Work Session End | ❌ Broken | MEDIUM | Technicians |
| Active Work Check | ❌ Broken | LOW | Technicians |
| Presence Update | ❌ Broken | HIGH | All users |
| Online Technicians | ❌ Broken | MEDIUM | All users |
| AI Context Memory | ❌ Broken | HIGH | All users |

---

## 🔧 FIX PRIORITY ORDER

### Phase 1: Critical User Experience (DO NOW) 🚨
1. `escalate_to_ticket()` - Users need ticket creation
2. `get_chat_history()` - Chat history essential
3. `get_conversation_context()` - AI needs context
4. `update_presence()` - Online status critical

### Phase 2: Core Functionality (NEXT) ⚡
5. `admin_send_direct_message()` - Admin communication
6. `start_work_session()` - Technician logging
7. `end_work_session()` - Technician logging
8. `get_active_work_session()` - Status display

### Phase 3: Admin Features (LATER) 📊
9. `monthly_report()` - Complex migration needed
10. `custom_date_report()` - Complex migration needed
11. `get_online_technicians()` - Can use Supabase version

---

## 💡 RECOMMENDED FIX STRATEGY

### For Simple CRUD Operations:
```python
# OLD (SQLite)
conn = get_db_connection()
result = conn.execute('SELECT * FROM table WHERE id = ?', (id,)).fetchone()
conn.close()

# NEW (Supabase)
response = db.client.table('table').select('*').eq('id', id).execute()
result = response.data[0] if response.data else None
```

### For Inserts:
```python
# OLD (SQLite)
cursor = conn.execute('INSERT INTO table (col1, col2) VALUES (?, ?)', (val1, val2))
new_id = cursor.lastrowid
conn.commit()
conn.close()

# NEW (Supabase)
response = db.client.table('table').insert({'col1': val1, 'col2': val2}).execute()
new_id = response.data[0]['id']  # Auto-generated ID
```

### For Updates:
```python
# OLD (SQLite)
conn.execute('UPDATE table SET col1 = ? WHERE id = ?', (value, id))
conn.commit()
conn.close()

# NEW (Supabase)
db.client.table('table').update({'col1': value}).eq('id', id).execute()
```

### For Complex Queries with JOINs:
```python
# OLD (SQLite JOIN)
result = conn.execute('''
    SELECT u.*, p.status 
    FROM user u 
    JOIN presence p ON u.userid = p.userid 
    WHERE ...
''')

# NEW (Supabase - fetch separately)
users_response = db.client.table('user').select('*').eq('role', 'technician').execute()
presence_response = db.client.table('user_presence').select('*').eq('status', 'online').execute()

# Join in Python
online_users = [u for u in users_response.data if any(p['userid'] == u['userid'] for p in presence_response.data)]
```

---

## 🚀 DEPLOYMENT CHECKLIST

After fixing each function:

1. ✅ Test locally with `.env` pointing to Supabase
2. ✅ Commit changes: `git commit -m "Fix: Migrate <function> to Supabase"`
3. ✅ Push to GitHub: `git push origin main`
4. ✅ Wait for Vercel deployment (2-3 min)
5. ✅ Test on production
6. ✅ Check Vercel function logs for errors

---

## 📝 QUICK FIX TEMPLATES

### Template 1: Simple Select
```python
@app.route('/api/example')
@login_required
def example_function():
    try:
        if not db.client:
            return jsonify({'error': 'Database connection failed'}), 500
        
        item_id = request.args.get('id')
        
        # Supabase query
        response = db.client.table('your_table').select('*').eq('id', item_id).execute()
        
        if not response.data:
            return jsonify({'error': 'Not found'}), 404
        
        return jsonify({'success': True, 'data': response.data[0]})
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500
```

### Template 2: Insert with Auto-ID
```python
@app.route('/api/create', methods=['POST'])
@login_required
def create_item():
    try:
        data = request.get_json()
        
        # Supabase insert
        response = db.client.table('your_table').insert({
            'user_id': session.get('user_id'),
            'content': data.get('content'),
            'status': 'active'
        }).execute()
        
        new_id = response.data[0]['id']
        
        return jsonify({'success': True, 'id': new_id})
    
    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({'error': str(e)}), 500
```

---

## 🎯 NEXT STEPS

1. **Start with Phase 1** (critical user features)
2. **Test each fix individually** before moving to next
3. **Deploy incrementally** - don't fix everything at once
4. **Monitor Vercel logs** after each deployment

**Want me to fix these for you?** I can migrate all of them to Supabase systematically!

---

**Last Updated**: March 14, 2026  
**Total SQLite Functions**: 12  
**Already Fixed**: 3  
**Remaining**: 11  
**Estimated Fix Time**: 30-45 minutes
