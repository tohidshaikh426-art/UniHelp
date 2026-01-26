# UniHelp IT Helpdesk Deployment Guide

## Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed
- Git installed

## Local Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables:
   - Create a `.env` file with:
     ```
     GEMINI_API_KEY=your_gemini_api_key
     ```

3. Run locally:
   ```bash
   python app.py
   ```

## Deployment to Heroku

### 1. Prepare the App
- Ensure `requirements.txt` includes all dependencies
- `Procfile` and `runtime.txt` are created
- Database will be created automatically on first run

### 2. Deploy
```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-app-name

# Set environment variables
heroku config:set GEMINI_API_KEY=your_gemini_api_key
heroku config:set SECRET_KEY=your-secure-random-secret-key
heroku config:set FLASK_ENV=production

# For email (update with real credentials)
heroku config:set MAIL_USERNAME=your-email@gmail.com
heroku config:set MAIL_PASSWORD=your-app-password

# Deploy
git add .
git commit -m "Ready for deployment"
git push heroku main

# Open app
heroku open
```

### 3. Post-Deployment
- Visit the app URL
- Login with default admin: `admin@unihelp.com` / `admin123`
- Change default passwords immediately

## Production Notes
- Change `app.secret_key` in `app.py` to a secure random string
- Use a production database (Heroku Postgres) for scalability
- Set up proper logging and monitoring
- Configure domain and SSL if needed

## Default Users
- Admin: admin@unihelp.com / admin123
- Technician: tech@unihelp.com / tech123
- Staff: staff@unihelp.com / staff123
- Student: student@unihelp.com / student123