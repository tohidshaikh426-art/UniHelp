# Quick Fix for Admin Login Issue

## Problem
Admin login shows "Invalid credentials" on Vercel deployment.

## Root Cause
Password hash mismatch between local and production Supabase.

---

## ✅ SOLUTION - Update Password in Supabase Dashboard

### Step 1: Go to Supabase Dashboard
Visit: https://supabase.com/dashboard/project/upfxdxzsmbitluakzajc/editor

### Step 2: Open User Table
1. Click **"Table Editor"** in left sidebar
2. Click **"user"** table

### Step 3: Find Admin User
1. Look for row with email: `admin@unihelp.com`
2. Click **"Edit"** (pencil icon) on that row

### Step 4: Update Password Hash
Replace the entire `passwordhash` field with this exact value:

```
pbkdf2:sha256:600000$mN2yyDx42PWTdufJ$663fae6291637ae0e8694992bd41127c58fe518b1502ab5bdbeceea7864d778c
```

### Step 5: Save Changes
Click **"Save"** button

### Step 6: Test Login
Go to your Vercel app and login with:
- **Email:** admin@unihelp.com
- **Password:** admin123

---

## 🔍 Alternative: Create New Admin via SQL

If the above doesn't work, run this SQL in Supabase SQL Editor:

```sql
-- Delete old admin (if exists)
DELETE FROM "user" WHERE email = 'admin@unihelp.com';

-- Create new admin with known password
INSERT INTO "user" (
    name, 
    email, 
    passwordhash, 
    role, 
    isapproved,
    created_at
) VALUES (
    'Admin User',
    'admin@unihelp.com',
    'pbkdf2:sha256:600000$mN2yyDx42PWTdufJ$663fae6291637ae0e8694992bd41127c58fe518b1502ab5bdbeceea7864d778c',
    'admin',
    true,
    NOW()
);
```

---

## ✅ Verification Steps

After updating:

1. **Clear browser cache** (Ctrl+Shift+Delete)
2. **Logout** if logged in
3. **Login again** with:
   - Email: admin@unihelp.com
   - Password: admin123

---

## 🐛 Still Not Working?

### Check Vercel Function Logs:
1. Go to Vercel Dashboard → Your Project
2. Click **"Function Logs"** tab
3. Look for error messages when you try to login

### Common Issues:

**Issue:** "User not found"
- **Fix:** Verify user exists in Supabase Table Editor

**Issue:** "Password hash mismatch"
- **Fix:** Copy the EXACT hash above (no extra spaces)

**Issue:** "Connection timeout"
- **Fix:** Check SUPABASE_URL in Vercel environment variables

---

## 📝 For Future Reference

To generate password hashes:
```python
from werkzeug.security import generate_password_hash
hash = generate_password_hash('your_password')
print(hash)
```

---

**After fixing, the login should work immediately!** ✅
