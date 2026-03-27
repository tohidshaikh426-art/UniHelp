#!/usr/bin/env python3
"""
Test script to verify AI chatbot functionality
Run this to check if your Gemini API key is working
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

print("🔍 Testing UniHelp AI Chatbot Configuration\n")
print("=" * 60)

# Check 1: Environment Variables
print("\n1️⃣  Checking Environment Variables...")
gemini_key = os.getenv('GEMINI_API_KEY')
if gemini_key:
    print(f"✅ GEMINI_API_KEY found: {gemini_key[:15]}...{gemini_key[-5:]}")
else:
    print("❌ GEMINI_API_KEY NOT FOUND!")
    print("   You need to add it to your .env file or Vercel environment variables")

# Check 2: Configure Gemini API
print("\n2️⃣  Configuring Gemini API...")
try:
    if gemini_key:
        genai.configure(api_key=gemini_key)
        print("✅ API configured successfully")
    else:
        print("⏭️  Skipping API configuration (no key)")
except Exception as e:
    print(f"❌ API configuration failed: {e}")

# Check 3: Test Model Loading
print("\n3️⃣  Testing Model Loading...")
try:
    if gemini_key:
        # Try flash model (faster, free tier friendly)
        model_flash = genai.GenerativeModel('gemini-1.5-flash')
        print("✅ gemini-1.5-flash loaded successfully")
        
        # Try pro model (what your app uses)
        model_pro = genai.GenerativeModel('gemini-1.5-pro')
        print("✅ gemini-1.5-pro loaded successfully")
    else:
        print("⏭️  Skipping model loading (no key)")
except Exception as e:
    print(f"❌ Model loading failed: {e}")

# Check 4: Test API Call
print("\n4️⃣  Testing API Call with Simple Query...")
try:
    if gemini_key:
        model = genai.GenerativeModel('gemini-1.5-flash')
        response = model.generate_content("Hi, are you working? Reply with 'Yes, I am working!'")
        print(f"✅ API call successful!")
        print(f"   Response: {response.text.strip()}")
    else:
        print("⏭️  Skipping API test (no key)")
except Exception as e:
    print(f"❌ API call failed: {e}")
    print("   Possible reasons:")
    print("   - Invalid API key")
    print("   - API quota exceeded")
    print("   - Network connectivity issues")
    print("   - API key permissions restricted")

# Summary
print("\n" + "=" * 60)
print("📊 SUMMARY:")
if gemini_key:
    print("✅ Your Gemini API key is configured")
    print("✅ You can use AI chatbot features")
    print("\n💡 NEXT STEPS:")
    print("   1. Make sure this .env file is NOT committed to git")
    print("   2. For Vercel deployment, add GEMINI_API_KEY to Vercel environment variables")
    print("   3. Go to Vercel Dashboard > Your Project > Settings > Environment Variables")
else:
    print("❌ No API key found")
    print("\n💡 FIX:")
    print("   1. Get API key from: https://makersuite.google.com/app/apikey")
    print("   2. Add to .env file: GEMINI_API_KEY=your_key_here")
    print("   3. For Vercel: Add to Vercel environment variables")

print("\n" + "=" * 60)
