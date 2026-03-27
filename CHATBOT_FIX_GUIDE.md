# 🔧 CHATBOT NOT WORKING - FIX GUIDE

## 🚨 PROBLEM IDENTIFIED

Your Gemini API key has been **compromised/leaked** and Google has disabled it.

**Error:** `403 Your API key was reported as leaked. Please use another API key.`

---

## ✅ SOLUTION (Follow These Steps)

### Step 1: Get a NEW Gemini API Key

1. **Go to Google AI Studio:** https://aistudio.google.com/app/apikey
2. **Click "Create API Key"** button
3. **Copy the new key** (it will look like: `AIzaSy...`)
4. **Save it securely** (password manager, notepad, etc.)

---

### Step 2: Update Local Development

1. Open your `.env` file in the UniHelp project folder
2. Replace the old key with the new one:
   ```
   GEMINI_API_KEY=your_new_api_key_here
   ```
3. Save the file
4. **Test locally:**
   ```bash
   python test_ai_chatbot.py
   ```
   You should see: `✅ API call successful!`

---

### Step 3: Update Vercel Deployment ⭐ CRITICAL

Since your app is deployed on Vercel, you MUST update the environment variable there:

#### Option A: Via Vercel Dashboard (Recommended)

1. **Go to Vercel:** https://vercel.com/dashboard
2. **Select your UniHelp project**
3. **Click "Settings"** tab at the top
4. **Click "Environment Variables"** in the left sidebar
5. **Click "Add Environment Variable"** or edit existing `GEMINI_API_KEY`
6. **Enter:**
   - Name: `GEMINI_API_KEY`
   - Value: `your_new_api_key_here`
7. **Click "Save"**
8. **Redeploy the project:**
   - Go to "Deployments" tab
   - Click on the latest deployment
   - Click the **"..."** menu
   - Click **"Redeploy"**

#### Option B: Via Vercel CLI (Alternative)

If you have Vercel CLI installed:
```bash
vercel env add GEMINI_API_KEY
# Follow the prompts
vercel --prod
```

---

### Step 4: Verify It's Working

1. **Wait 2-3 minutes** after redeployment completes
2. **Open your deployed app** on Vercel
3. **Login** as any user (admin, student, staff, technician)
4. **Navigate to the AI Chatbot page**
5. **Send a test message:** "Hi, are you working?"
6. **You should get an AI response!** ✅

---

## 🔒 SECURITY BEST PRACTICES

### To Prevent Future Key Leaks:

1. **NEVER commit `.env` file to Git**
   - Make sure `.env` is in your `.gitignore` file
   - Your `.gitignore` already has this covered ✅

2. **Use Vercel Environment Variables**
   - Store sensitive keys in Vercel dashboard, not in code
   - Only use `.env` for local development

3. **Rotate Keys Periodically**
   - Change API keys every few months
   - Immediately if you suspect a leak

4. **Check for Accidental Exposure**
   - Search GitHub for your key: `https://github.com/search?q=YOUR_API_KEY`
   - Use tools like GitGuardian to monitor

---

## 📊 TROUBLESHOOTING

### If chatbot still doesn't work after getting new key:

**Check 1: Verify API Key is Active**
```bash
python test_ai_chatbot.py
```
Should show all green checkmarks ✅

**Check 2: Check Vercel Logs**
1. Go to Vercel Dashboard → Your Project
2. Click on latest deployment
3. Click "View Function Logs"
4. Look for errors related to Gemini API

**Check 3: Test Different Model**
If `gemini-1.5-pro` doesn't work, try `gemini-1.5-flash` (faster, free tier):
- In `app.py` line 33, change:
  ```python
  model = genai.GenerativeModel('gemini-1.5-flash')
  ```

**Check 4: Check API Quota**
1. Go to: https://aistudio.google.com/app/quota
2. Check if you've exceeded rate limits
3. Free tier: 15 requests per minute, 1 million tokens per minute

---

## 🎯 QUICK SUMMARY

**What happened?**
- Your API key was leaked (possibly committed to git accidentally)
- Google disabled it for security

**How to fix?**
1. Get new API key from Google AI Studio
2. Update local `.env` file
3. Update Vercel environment variables
4. Redeploy on Vercel

**Time needed:** 5-10 minutes

---

## 📞 NEED HELP?

If you're still stuck:
1. Run `python test_ai_chatbot.py` and share the output
2. Check Vercel function logs for errors
3. Make sure `.env` is NOT in git (check `.gitignore`)

---

**Good luck!** 🚀 The chatbot will be working once you get the new API key and update Vercel.
