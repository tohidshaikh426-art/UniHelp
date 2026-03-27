# 🔐 Forgot Password Feature - Setup Guide

## ✅ What's Been Implemented

A complete password reset system with:
1. **Secure token generation** (256-bit tokens)
2. **Email delivery** via Flask-Mail
3. **Token expiration** (1 hour for security)
4. **Password validation** (minimum 8 characters)
5. **One-time use tokens** (prevents reuse)
6. **Beautiful responsive UI** (matches your existing design)

---

## 📋 STEP-BY-STEP SETUP

### Step 1: Create Database Table ⭐ CRITICAL

1. Go to **Supabase Dashboard**: https://app.supabase.com/
2. Select your project: `upfxdxzsmbitluakzajc`
3. Click **"SQL Editor"** → **"New Query"**
4. Copy the SQL from [`password_reset_migration.sql`](file://c:\Users\Asus\OneDrive\Desktop\UniHelp\password_reset_migration.sql)
5. Paste into SQL Editor
6. Click **"Run"** or press Ctrl+Enter
7. Should say: **"Success. No rows returned"**

**Verification:**
```sql
SELECT * FROM password_reset_tokens LIMIT 1;
```

---

### Step 2: Configure Email Settings

The feature uses Gmail SMTP by default. Update these in Vercel:

#### Option A: Using Gmail (Recommended for simplicity)

1. **Create App Password** (if using Gmail):
   - Go to: https://myaccount.google.com/apppasswords
   - Select "Mail" and "Other (Custom name)"
   - Enter "UniHelp" as the name
   - Click "Generate"
   - Copy the 16-character password

2. **Update Vercel Environment Variables**:
   - Go to Vercel Dashboard → Your Project → Settings → Environment Variables
   - Add/Edit:
   ```
   MAIL_USERNAME=unihelp.project@gmail.com
   MAIL_PASSWORD=your_16_char_app_password
   ```

#### Option B: Using Your Own Email

Update in `.env` file (for local) and Vercel (for production):
```
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
```

---

### Step 3: Test Locally

1. **Start your app locally:**
   ```bash
   python app.py
   ```

2. **Go to login page:** http://localhost:5000/login
3. **Click "Forgot password?"** link
4. **Enter an email** (use a real email you can access)
5. **Check your inbox** for the reset email
6. **Click the reset link** in the email
7. **Set a new password**
8. **Login** with the new password

---

### Step 4: Deploy to Vercel

The code is already committed, so just:

1. **Push to GitHub** (I'll do this for you)
2. **Vercel will auto-deploy**
3. **Wait 2-3 minutes** for deployment to complete
4. **Test on production**

---

## 🎯 HOW IT WORKS

### User Flow:

1. **User clicks "Forgot password?"** on login page
2. **Enters their email** address
3. **System checks** if email exists (doesn't reveal if it does for security)
4. **Generates secure token** (256-bit random string)
5. **Sends email** with reset link (expires in 1 hour)
6. **User clicks link** → validates token
7. **User enters new password** (min 8 chars, must match confirmation)
8. **Password updated** in database
9. **Token marked as used** (can't be reused)
10. **User redirected to login** with success message

### Security Features:

✅ **256-bit secure tokens** (using `secrets.token_urlsafe()`)  
✅ **1-hour expiration** (auto-deletes expired tokens)  
✅ **One-time use** (tokens marked as used after reset)  
✅ **No user enumeration** (doesn't reveal if email exists)  
✅ **HTTPS required** (in production, tokens sent securely)  
✅ **Password validation** (minimum length, confirmation required)  

---

## 📁 FILES CREATED/MODIFIED

### New Files:
1. **`password_reset_migration.sql`** - Database migration script
2. **`templates/forgot_password.html`** - Forgot password form
3. **`templates/reset_password.html`** - Reset password form
4. **`FORGOT_PASSWORD_SETUP.md`** - This guide

### Modified Files:
1. **`supabase_client.py`** - Added password reset methods:
   - `create_password_reset_token()`
   - `get_reset_token_by_token()`
   - `mark_token_as_used()`
   - `delete_expired_tokens()`

2. **`app.py`** - Added routes:
   - `/forgot-password` (GET/POST)
   - `/reset-password/<token>` (GET/POST)

3. **`templates/login.html`** - Added "Forgot password?" link

---

## 🧪 TESTING CHECKLIST

### Local Testing:
- [ ] Database table created successfully
- [ ] Email configuration works
- [ ] Can request password reset
- [ ] Received email with reset link
- [ ] Reset link works and shows form
- [ ] Can set new password
- [ ] Can login with new password
- [ ] Old password no longer works
- [ ] Token expires after 1 hour
- [ ] Used token cannot be reused

### Production Testing (after Vercel deploy):
- [ ] All of the above on production
- [ ] Email links point to correct Vercel URL
- [ ] HTTPS enabled (Vercel does this automatically)

---

## 🔧 EMAIL CONFIGURATION TROUBLESHOOTING

### If emails aren't sending:

**Check 1: Verify environment variables**
```bash
# Locally in .env
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password

# In Vercel dashboard
Settings → Environment Variables
```

**Check 2: Test email connection locally**
```python
from flask_mail import Mail, Message
from app import app

with app.app_context():
    msg = Message('Test', recipients=['your-email@example.com'])
    msg.body = 'This is a test'
    mail.send(msg)
    print("Email sent!")
```

**Check 3: Check Vercel logs**
- Go to Vercel Dashboard → Your Project → Deployments
- Click latest deployment → "View Function Logs"
- Look for email sending errors

**Common Gmail Issues:**
- ❌ Using regular password instead of App Password
- ❌ Two-factor authentication not enabled
- ❌ App password generated for wrong service

**Fix:**
1. Enable 2FA on Google account
2. Generate new App Password for "Mail"
3. Use the 16-character password (no spaces)

---

## 📊 DATABASE SCHEMA

### password_reset_tokens Table:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER (PK) | Auto-increment ID |
| `email` | VARCHAR(255) | User's email address |
| `token` | VARCHAR(255) | Secure random token (unique) |
| `expires_at` | TIMESTAMP | Token expiration time |
| `used` | BOOLEAN | Whether token has been used |
| `created_at` | TIMESTAMP | When token was created |

**Indexes:**
- `idx_password_reset_tokens_email` - Fast lookup by email
- `idx_password_reset_tokens_token` - Fast token validation
- `idx_password_reset_tokens_expires_at` - Efficient cleanup

---

## 🚀 QUICK START COMMANDS

### Local Development:
```bash
# 1. Make sure .env has email credentials
# 2. Run the SQL migration in Supabase
# 3. Start the app
python app.py

# 4. Test at http://localhost:5000/login
```

### Production (Vercel):
```bash
# Already deployed! Just:
# 1. Wait for auto-deployment
# 2. Test at your Vercel URL
# https://your-project.vercel.app/login
```

---

## 💡 BEST PRACTICES

### For Users:
- ✅ Use strong, unique passwords
- ✅ Reset links expire in 1 hour for security
- ✅ Don't share reset links
- ✅ Request a new link if expired

### For Admins:
- ✅ Monitor password reset requests
- ✅ Check logs for suspicious activity
- ✅ Ensure email delivery is working
- ✅ Review token usage patterns

---

## 🆘 TROUBLESHOOTING

### Issue: "Invalid or expired reset token"
**Cause:** Token expired or already used  
**Fix:** Request a new password reset

### Issue: Email not received
**Causes:**
- Wrong email address entered
- Email in spam/junk folder
- Email service blocking
- SMTP credentials incorrect

**Fix:**
1. Check spam folder
2. Verify email address
3. Check SMTP credentials in Vercel
4. Try a different email provider

### Issue: "Failed to update password"
**Cause:** Database error or user not found  
**Fix:** Check Supabase connection and logs

---

## 📞 NEED HELP?

If you encounter issues:

1. Check Vercel function logs for errors
2. Verify database table exists in Supabase
3. Test email configuration locally first
4. Ensure all environment variables are set

---

**Your forgot password feature is ready to use!** 🎉

Just run the SQL migration and configure email settings, then you're all set!
