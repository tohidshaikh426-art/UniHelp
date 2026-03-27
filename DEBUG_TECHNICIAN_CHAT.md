# 🔍 Debug: Technician Not Receiving Chats

## 📊 STEP-BY-STEP DIAGNOSIS

### Step 1: Check Vercel Function Logs

1. **Go to Vercel Dashboard**: https://vercel.com/dashboard/tohidshaikh426-art/UniHelp
2. **Click "Deployments"** → Latest deployment
3. **Click "View Function Logs"**
4. **Filter by**: `technician/new_chats`

**What to look for:**
```
🔍 Checking chats for technician ID: X
📊 Found Y active chats
💬 Chat found: {...}
✅ Returning: {...}
```

**If you see:**
- ✅ "Found 1 active chats" → Query working, check frontend
- ❌ "Found 0 active chats" → No chats in database or wrong technician ID

---

### Step 2: Test the API Directly

Open your browser console (F12) while logged in as technician:

```javascript
// Check API response
fetch('/technician/new_chats')
  .then(r => r.json())
  .then(d => console.log('API Response:', d));
```

**Expected response:**
```json
{
  "success": true,
  "new_chats": [],
  "count": 0,
  "has_new_chat": false,
  "debug": {
    "technician_id": 5,
    "total_found": 0
  }
}
```

**Check:**
- Is `technician_id` correct? (should match your technician user ID)
- Is `total_found` > 0? (means chats exist in DB)

---

### Step 3: Verify Live Chat Was Created

When admin sends a chat, check if it's actually created:

**In Supabase SQL Editor:**
```sql
-- Check if live_chat was created
SELECT * FROM live_chat 
WHERE status = 'active'
ORDER BY started_at DESC
LIMIT 5;

-- Check for YOUR technician specifically
SELECT * FROM live_chat 
WHERE technicianid = YOUR_TECHNICIAN_ID 
AND status = 'active';
```

**Replace `YOUR_TECHNICIAN_ID` with actual ID from session.**

---

### Step 4: Check Admin Flow

When admin clicks "Connect with Technician", check what happens:

1. **Open browser console** (F12) on admin page
2. **Click "Connect with Technician"**
3. **Look for network request** to `/api/chat/request_technician_chat`
4. **Check response:**

**Success:**
```json
{
  "success": true,
  "type": "live_chat",
  "technician_name": "John Doe",
  "technician_id": 5,
  "message": "✅ Connected to John Doe!..."
}
```

**Failure:**
```json
{
  "success": false,
  "error": "No technicians available"
}
```

---

### Step 5: Check Technician Availability

The system only assigns chats to technicians who are:
1. ✅ **Online** (status = 'online' in user_presence)
2. ✅ **Active recently** (last_seen within 10 minutes for admin/staff requests)
3. ✅ **Not in another chat** (no active live_chat records)

**Check in Supabase:**
```sql
-- Check if technician is online
SELECT * FROM user_presence 
WHERE userid = YOUR_TECHNICIAN_ID;

-- Check if technician is in active chat
SELECT * FROM live_chat 
WHERE technicianid = YOUR_TECHNICIAN_ID 
AND status = 'active';
```

---

## 🎯 COMMON ISSUES & FIXES

### Issue 1: "Found 0 active chats"

**Cause:** No chats assigned to this technician

**Fix:**
1. Make sure admin actually sent a chat
2. Check that technician was selected/available
3. Verify live_chat record exists in database

---

### Issue 2: Wrong Technician ID

**Cause:** Session has wrong/different technician ID

**Fix:**
1. Log out and log back in as technician
2. Check session['user_id'] matches technician's userid in database
3. Make sure you're testing with approved technician account

---

### Issue 3: Technician Not Available

**Cause:** Technician marked as offline or busy

**Fix:**
1. Visit any page as technician to update presence (auto-updates every page load)
2. Wait for presence to show as 'online' (happens automatically)
3. End any other active chats first

---

### Issue 4: Chat Created But Not Showing

**Cause:** Frontend not polling or JavaScript error

**Fix:**
1. Open browser console (F12)
2. Look for JavaScript errors
3. Check Network tab - should see requests to `/technician/new_chats` every 3 seconds
4. Check if requests are returning data

---

## 🧪 COMPLETE TEST FLOW

### Test Scenario:

1. **Setup:**
   - Browser 1: Login as **Admin** (admin@unihelp.com)
   - Browser 2: Login as **Technician** (tech@unihelp.com)

2. **On Technician Browser:**
   - Go to: `/technician/live_chats`
   - Open Console (F12)
   - Should see: "🔍 Checking chats for technician ID: X" every 3 seconds

3. **On Admin Browser:**
   - Start AI chatbot conversation
   - Click "Connect with Technician"
   - Watch for response

4. **Watch Technician Browser:**
   - Within 3 seconds should see notification
   - Page should auto-refresh
   - New chat should appear

---

## 📝 DEBUGGING CHECKLIST

- [ ] Technician account exists and is approved (`isapproved = true`)
- [ ] Technician role is set correctly (`role = 'technician'`)
- [ ] Presence record exists and shows online
- [ ] No other active chats blocking assignment
- [ ] Admin successfully triggered "Connect with Technician"
- [ ] API returns success when creating live_chat
- [ ] live_chat record exists in database
- [ ] Technician ID in session matches assigned technician
- [ ] Frontend JavaScript running without errors
- [ ] Polling requests happening every 3 seconds

---

## 🚀 QUICK FIX COMMANDS

### Check everything in one query:
```sql
-- Comprehensive check
SELECT 
    lc.livechatid,
    lc.status,
    lc.started_at,
    u.name as technician_name,
    up.status as presence_status,
    up.last_seen
FROM live_chat lc
JOIN user u ON lc.technicianid = u.userid
LEFT JOIN user_presence up ON u.userid = up.userid
WHERE lc.technicianid = YOUR_TECHNICIAN_ID
AND lc.status = 'active';
```

### Force technician online:
```sql
-- Update presence to online NOW
INSERT INTO user_presence (userid, status, last_seen)
VALUES (YOUR_TECHNICIAN_ID, 'online', NOW())
ON CONFLICT (userid) 
DO UPDATE SET 
    status = 'online',
    last_seen = NOW();
```

---

## 💡 STILL NOT WORKING?

Share these details:
1. **Vercel logs output** (from Step 1)
2. **API response** (from Step 2)
3. **Database query result** (from Step 3)
4. **Browser console errors** (F12 → Console tab)

This will help identify the exact issue! 🎯
