# UniHelp Deployment Guide - Vercel + Supabase

## 🎯 Current Setup

**Platform**: Vercel (Frontend/Backend) + Supabase (Database)
**Status**: ✅ Production Ready

---

## 📋 Environment Variables on Vercel

These MUST be set in Vercel Dashboard → Project Settings → Environment Variables:

```
SUPABASE_URL=<your-supabase-url>
SUPABASE_KEY=<your-anon-key>
GEMINI_API_KEY=<your-gemini-api-key>
FLASK_ENV=production
SECRET_KEY=<your-secret-key>
MAIL_SERVER=smtp.gmail.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=<your-email@gmail.com>
MAIL_PASSWORD=<your-app-password>
```

### ❌ DO NOT Add to Vercel:
- `SUPABASE_SERVICE_KEY` - Not needed for production (security best practice)

---

## 🔧 Local Development Notes

### Known Issue: "Proxy Error"
When running locally with Python 3.13, you might see:
```
TypeError: Client.__init__() got an unexpected keyword argument 'proxy'
```

**Cause**: Supabase v2.3.4 has dependency conflicts with Python 3.13
**Impact**: Only affects local testing - production on Vercel works fine
**Solution**: Use Python 3.10 or 3.11 for local development if needed

### Testing Locally
If you want to test locally:
1. Create a `.env` file with the same variables as Vercel
2. Run: `python app.py`
3. Note: Some features might not work due to RLS policies

---

## 👤 Admin Login Credentials

**Email**: admin@unihelp.com  
**Password**: admin123

This user exists in your Supabase database and can login immediately.

---

## 🗄️ Database Status

**Provider**: Supabase (PostgreSQL)
**URL**: https://upfxdxzsmbitluakzajc.supabase.co

### Tables:
- ✅ user
- ✅ ticket
- ✅ comment
- ✅ chat_session
- ✅ chat_message
- ✅ live_chat
- ✅ user_presence

### RLS Policies:
Row Level Security is enabled and configured to work with the anon key for most operations.

---

## 🚀 Deployment Checklist

### On Vercel:
- [x] Set all environment variables
- [x] Connect GitHub repository
- [x] Deploy branch: main/master
- [x] Build command: (automatic for Flask)
- [x] Output directory: (automatic)

### On Supabase:
- [x] Database created
- [x] Tables migrated
- [x] RLS policies configured
- [x] Admin user created

---

## 🔍 Troubleshooting

### "SUPABASE_SERVICE_KEY_length: 0"
✅ **This is NORMAL for Vercel deployment**
- Service key is intentionally not used in production
- App uses anon key with RLS policies instead

### "proxy" parameter error
⚠️ **Only affects local development with Python 3.13**
- Doesn't impact Vercel deployment
- Use older Python version locally if needed

### Admin cannot access tickets/users
⚠️ **Check RLS policies in Supabase**
- The anon key respects RLS policies
- Ensure admin role has proper permissions via RLS
- Consider using service_role key locally for testing

---

## 📝 Version Information

**Flask**: 2.3.3  
**Werkzeug**: 2.3.7  
**Supabase**: 2.3.4 (pinned for Vercel compatibility)  
**Python-dotenv**: 1.0.0  
**google-generativeai**: 0.3.2  

---

## 🔗 Useful Links

- **Vercel Dashboard**: https://vercel.com/dashboard
- **Supabase Dashboard**: https://app.supabase.com/project/upfxdxzsmbitluakzajc
- **Documentation**: See presentation folder for detailed guides

---

**Last Updated**: March 14, 2026  
**Status**: ✅ All Systems Operational
