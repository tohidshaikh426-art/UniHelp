# Debug Login Issue - Step by Step

## Current Status:
✅ Admin user exists in Supabase
✅ Password hash is correct
✅ RLS policy allows SELECT with anon key
✅ Local testing works

## Problem:
❌ Vercel deployment still shows "Invalid credentials"

---

## 🔍 Let's Check What's Happening

### Step 1: Check Vercel Function Logs

1. Go to: https://vercel.com/dashboard
2. Click on your UniHelp project
3. Click **"Function Logs"** tab
4. Try to login on your Vercel app
5. Look for ERROR messages in the logs

**What do you see?**
- [ ] "User not found"
- [ ] "Password mismatch"  
- [ ] "Database connection error"
- [ ] Something else?

---

## 🛠️ Possible Issues & Fixes

### Issue 1: Vercel hasn't redeployed yet
**Fix:** Force redeploy
1. Go to Vercel → Deployments
2. Click ⋮ on latest deployment
3. Click "Redeploy"
4. Wait 2-3 minutes
5. Test again

### Issue 2: Environment variables wrong in Vercel
**Check:**
1. Vercel Dashboard → Settings → Environment Variables
2. Verify these exist and are correct:
   - `SUPABASE_URL` = `https://upfxdxzsmbitluakzajc.supabase.co`
   - `SUPABASE_KEY` = Anon key (starts with eyJ...)
   - `GEMINI_API_KEY` = Your Gemini key

**Important:** Make sure SUPABASE_KEY is the **ANON** key, NOT service_role!

### Issue 3: Cold cache in browser
**Fix:**
1. Open Vercel app in Incognito/Private window
2. Or clear browser cache (Ctrl+Shift+Delete)
3. Try login again

### Issue 4: App is using old code
**Fix:** Add debug message to verify code version

Let me add a temporary debug route to verify which code is running:

---

## 🧪 Quick Test - Create Debug Route

Run these commands to add a debug endpoint:

```python
# Add to app.py temporarily
@app.route('/debug')
def debug():
    from supabase_client import db
    admin = db.get_user_by_email('admin@unihelp.com')
    return {
        'admin_exists': admin is not None,
        'email': admin['email'] if admin else 'Not found',
        'is_approved': admin['isapproved'] if admin else False,
        'supabase_connected': db.client is not None
    }
```

Then:
1. Commit and push
2. Wait for deploy
3. Visit: `https://your-app.vercel.app/debug`
4. Check if it shows admin exists

---

## 📋 Checklist - Verify These NOW

### In Supabase Dashboard:
- [ ] User table has admin@unihelp.com
- [ ] isapproved = true (boolean, not string)
- [ ] role = 'admin'
- [ ] passwordhash starts with `pbkdf2:sha256:`

### In Vercel Dashboard:
- [ ] SUPABASE_URL is correct (no trailing /)
- [ ] SUPABASE_KEY is anon key (not service_role)
- [ ] All env vars are set for Production, Preview, AND Development

### In Browser:
- [ ] Using HTTPS (not HTTP)
- [ ] No browser extensions blocking requests
- [ ] Console shows no JavaScript errors (F12)

---

## 🎯 Next Steps

**Tell me:**
1. What does Vercel Function Logs show when you try to login?
2. Did you force redeploy after adding the RLS policy?
3. Are you testing in incognito mode?

**Most likely:** You need to force redeploy on Vercel so it picks up the RLS changes.
