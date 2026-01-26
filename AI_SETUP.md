# UniHelp AI Setup Guide

## Enabling AI-Powered Chatbot

The UniHelp chatbot can use Google's Gemini AI for more natural, conversational responses. Here's how to enable it:

### 1. Get a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key
4. Copy the API key (it starts with "AIzaSy...")

### 2. Set Environment Variable

**Windows:**
```cmd
set GEMINI_API_KEY=AIzaSyAwqiN2F5Ri5l6R8rTtd-aDhAKb-vV1pus
```

**Or create a .env file in the project root:**
```
GEMINI_API_KEY=AIzaSyAwqiN2F5Ri5l6R8rTtd-aDhAKb-vV1pus
```

### 3. Restart the Application

The app will automatically detect the API key and enable AI responses.

### 4. Verify AI is Working

- Visit `/api/chat/status` (requires login)
- Look for "AI-Powered (Gemini)" in the response
- Test the chatbot - responses should be more conversational

## Current Status

- **Without AI:** Uses intelligent pattern matching (still very helpful!)
- **With AI:** More natural, personalized responses like a real IT technician

## Troubleshooting

- **"API key not valid"**: Double-check your API key
- **Still using fallback**: Make sure the environment variable is set correctly
- **Rate limits**: Free tier has usage limits - consider upgrading for heavy use

## Cost

- Gemini AI has a generous free tier
- Monitor usage in Google Cloud Console if needed