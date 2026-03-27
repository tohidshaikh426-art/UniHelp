# 🔧 CHATBOT ERROR FIX - Database Schema Issue

## 🚨 PROBLEM IDENTIFIED

You have **TWO separate issues** preventing the chatbot from working:

### Issue 1: Leaked API Key (Already identified)
Your Gemini API key was compromised and disabled by Google.

### Issue 2: Database Schema Mismatch (NEW - Critical!) ⚠️
Your code is trying to insert a UUID string into an INTEGER column in Supabase.

**Error Message:**
```
invalid input syntax for type integer: "e0bd0987-63df-4e09-aadd-3ec43c172623"
```

**What's happening:**
- Your `chat_session.sessionid` column should be an **auto-incrementing INTEGER**
- But the code is generating a UUID string and trying to insert it
- Supabase rejects this because it expects an integer, not a UUID string

---

## ✅ COMPLETE FIX (Follow ALL Steps)

### Step 1: Fix Database Schema in Supabase ⭐ CRITICAL

1. **Go to Supabase Dashboard:** https://app.supabase.com/
2. **Select your project** (upfxdxzsmbitluakzajc)
3. **Click "SQL Editor"** in the left sidebar
4. **Click "New Query"**
5. **Copy and paste** the SQL from [`fix_supabase_schema.sql`](file://c:\Users\Asus\OneDrive\Desktop\UniHelp\fix_supabase_schema.sql)
6. **Click "Run"** (or press Ctrl+Enter)
7. **Verify success** - you should see "Success. No rows returned"

**What this does:**
- Drops old chat_session table with wrong schema
- Recreates it with auto-incrementing INTEGER sessionid
- Properly sets up foreign keys and indexes

---

### Step 2: Get NEW Gemini API Key

1. **Go to:** https://aistudio.google.com/app/apikey
2. **Click "Create API Key"**
3. **Copy the new key**
4. **Save it securely**

---

### Step 3: Update Local `.env` File

Open your `.env` file and update BOTH values:

```env
GEMINI_API_KEY=your_new_api_key_here
SUPABASE_URL=https://upfxdxzsmbitluakzajc.supabase.co
SUPABASE_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
```

**Where to get Supabase keys:**
1. Go to Supabase Dashboard
2. Click "Settings" (gear icon) → "API"
3. Copy the "anon public" key for `SUPABASE_KEY`
4. Copy the "service_role" key for `SUPABASE_SERVICE_KEY`

---

### Step 4: Test Locally

```bash
python test_ai_chatbot.py
```

Expected output:
```
✅ GEMINI_API_KEY found
✅ API configured successfully
✅ gemini-1.5-flash loaded successfully
✅ gemini-1.5-pro loaded successfully
✅ API call successful!
   Response: Yes, I am working!
```

---

### Step 5: Update Vercel Environment Variables ⭐ CRITICAL FOR DEPLOYMENT

1. **Go to Vercel Dashboard:** https://vercel.com/dashboard
2. **Select your UniHelp project**
3. **Click "Settings"** tab
4. **Click "Environment Variables"** in left sidebar
5. **Add/Edit these variables:**

| Variable Name | Value |
|--------------|-------|
| `GEMINI_API_KEY` | `your_new_api_key_here` |
| `SUPABASE_URL` | `https://upfxdxzsmbitluakzajc.supabase.co` |
| `SUPABASE_KEY` | `your_supabase_anon_key` |
| `SUPABASE_SERVICE_KEY` | `your_supabase_service_role_key` |

6. **Click "Save"** for each variable
7. **Redeploy the application:**
   - Go to "Deployments" tab
   - Click on latest deployment
   - Click "..." menu
   - Click **"Redeploy"**

---

### Step 6: Verify Everything Works

1. **Wait 2-3 minutes** after redeployment completes
2. **Open your deployed app** on Vercel
3. **Login** as any user (admin/student/staff/technician)
4. **Navigate to AI Chatbot page**
5. **Send a test message:** "Hi, are you working?"
6. **You should get an AI response!** ✅

---

## 📊 WHAT I FIXED IN YOUR CODE

### Changes to `app.py` (Lines 795-825)

**BEFORE (WRONG):**
```python
import uuid
new_session_id = str(uuid.uuid4())  # Creates UUID string

response = db.client.table('chat_session').insert({
    'sessionid': new_session_id,  # ❌ Trying to insert UUID into INTEGER column
    'userid': user_id,
    'status': 'active'
}).execute()
```

**AFTER (CORRECT):**
```python
# Let Supabase auto-generate sessionid as integer
response = db.client.table('chat_session').insert({
    'userid': user_id,  # ✅ Only provide userid and status
    'status': 'active'
}).execute()

session_id = response.data[0]['sessionid']  # ✅ Get auto-generated integer ID
```

---

## 🔍 WHY THIS HAPPENED

### Root Cause:
1. Your local SQLite database uses INTEGER primary keys (auto-increment)
2. But somewhere in development, the code was changed to use UUIDs
3. The code tries to manually generate UUIDs and insert them
4. Supabase PostgreSQL expects auto-incrementing integers
5. Type mismatch causes the error

### Why it worked locally but not on Vercel:
- **Local SQLite:** More lenient with type conversions
- **Supabase PostgreSQL:** Strict type checking, rejects UUID strings in INTEGER columns

---

## 📁 HELPFUL FILES I CREATED

1. **[fix_supabase_schema.sql](file://c:\Users\Asus\OneDrive\Desktop\UniHelp\fix_supabase_schema.sql)** - Run this in Supabase SQL Editor
2. **[test_ai_chatbot.py](file://c:\Users\Asus\OneDrive\Desktop\UniHelp\test_ai_chatbot.py)** - Test your API key and setup
3. **[CHATBOT_FIX_GUIDE.md](file://c:\Users\Asus\OneDrive\Desktop\UniHelp\CHATBOT_FIX_GUIDE.md)** - Previous guide for API key issue

---

## 🎯 QUICK CHECKLIST

Before testing, make sure you've done ALL of these:

- [ ] Ran `fix_supabase_schema.sql` in Supabase SQL Editor
- [ ] Got new Gemini API key from Google AI Studio
- [ ] Updated local `.env` file with new keys
- [ ] Tested locally with `python test_ai_chatbot.py`
- [ ] Updated ALL environment variables in Vercel dashboard
- [ ] Redeployed application on Vercel
- [ ] Waited 2-3 minutes after deployment
- [ ] Tested chatbot in deployed app

---

## 🚨 STILL NOT WORKING?

### Check Supabase Logs:
1. Go to Supabase Dashboard
2. Click "Logs" in left sidebar
3. Look for errors related to `chat_session` table

### Check Vercel Function Logs:
1. Go to Vercel Dashboard → Your Project
2. Click latest deployment
3. Click "View Function Logs"
4. Look for errors when you try to start a chat

### Common Issues:

**Issue:** Still getting UUID error
**Fix:** Make sure you ran the SQL migration script in Supabase

**Issue:** Getting "User not found" error  
**Fix:** Check that `session.get('user_id')` is returning correct integer

**Issue:** API key still not working
**Fix:** Double-check you copied the ENTIRE API key (no spaces or missing characters)

---

## 💡 PREVENTION TIPS

1. **Always use auto-incrementing integers** for primary keys in Supabase
2. **Don't manually set primary key values** - let the database handle it
3. **Test with PostgreSQL locally** (not just SQLite) to catch these issues early
4. **Use Supabase's built-in identity columns** for auto-increment

---

## 📞 NEED MORE HELP?

If you're still stuck after following ALL steps:

1. Share the output of `python test_ai_chatbot.py`
2. Share any error messages from Vercel function logs
3. Confirm you ran the SQL migration script successfully

---

**Good luck!** 🚀 Follow ALL steps in order and your chatbot will work perfectly!
