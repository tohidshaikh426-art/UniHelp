# 🎓 UniHelp - IT Helpdesk Management System

A comprehensive IT helpdesk solution built with Python Flask, featuring AI-powered support and role-based access control.

![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green.svg)
![SQLite](https://img.shields.io/badge/SQLite-3-orange.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## ✨ Features

### 🎯 Core Functionality
- **Role-Based Access Control** - Admin, Technician, Staff, Student roles
- **Ticket Management** - Complete lifecycle from creation to resolution
- **AI Chatbot** - Google Gemini-powered automated support
- **Live Chat** - Real-time technician-user communication
- **Work Logging** - Technician time tracking
- **Analytics Dashboard** - Monthly reports and statistics

### 🔐 Security
- Password hashing with Werkzeug
- Session management
- Role-based permissions
- Input validation

### 📊 Database
- 11 normalized tables
- Audit trail tracking
- Foreign key constraints
- Pre-computed reports cache

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- pip

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/YOUR_USERNAME/UniHelp.git
   cd UniHelp
   ```

2. **Create virtual environment**
   ```bash
   python -m venv .venv
   .venv\Scripts\Activate  # Windows
   source .venv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   # Copy the example file
   copy .env.example .env
   
   # Edit .env and add your Gemini API key
   ```

5. **Initialize database**
   ```bash
   python db_init.py
   ```

6. **Run the application**
   ```bash
   python app.py
   ```

7. **Access the application**
   - Open browser: `http://localhost:5000`

---

## 👥 Default Users

| Role | Email | Password |
|------|-------|----------|
| Admin | admin@unihelp.com | admin123 |
| Technician | tech@unihelp.com | tech123 |
| Staff | staff@unihelp.com | staff123 |
| Student | student@unihelp.com | student123 |

⚠️ **Change these passwords in production!**

---

## 📁 Project Structure

```
UniHelp/
├── app.py                      # Main Flask application
├── db_init.py                  # Database initialization
├── requirements.txt            # Python dependencies
├── .env                        # Environment variables (not committed)
├── .env.example               # Example environment file
├── static/                     # Static files
│   ├── css/
│   ├── js/
│   └── img/
├── templates/                  # HTML templates
│   ├── admin/
│   ├── technician/
│   ├── user/
│   └── ...
├── uploads/                    # File uploads
└── unihelp.db                 # SQLite database (not committed)
```

---

## 🛠️ Technologies Used

- **Backend:** Python 3.10+, Flask 2.3.3
- **Database:** SQLite3
- **AI Integration:** Google Gemini API
- **Email:** Flask-Mail
- **Authentication:** Werkzeug security
- **Deployment:** Vercel (Serverless)

---

## 📊 Database Schema

The system uses 11 tables:
- `user` - User accounts with roles
- `ticket` - Support tickets
- `comment` - Ticket comments
- `chat_session` - AI chat sessions
- `chat_message` - Chat messages
- `chatbot_interaction` - AI interactions
- `live_chat` - Live chat sessions
- `technician_work_log` - Work time tracking
- `ticket_history` - Audit trail
- `monthly_reports_cache` - Cached analytics
- `user_presence` - Online status

---

## 🎯 Key Features

### Ticket Management
- Create, update, resolve tickets
- Priority levels (Low, Medium, High, Urgent)
- Status tracking (Open → In Progress → Resolved → Closed)
- File attachments support
- Satisfaction ratings

### AI Chatbot
- Google Gemini integration
- Automated first-line support
- Intent detection
- Escalation to human technicians

### Analytics
- Real-time dashboards
- Monthly reports
- Technician performance metrics
- Ticket resolution statistics

---

## 🔒 Security Considerations

- Passwords are hashed using bcrypt
- Environment variables for sensitive data
- Role-based access control on all routes
- SQL injection prevention via parameterized queries
- File upload validation

---

## 📝 License

This project is created as a final year project for educational purposes.

---

## 👨‍💻 Author

**Your Name**
- GitHub: [@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- Email: your.email@example.com

---

## 🙏 Acknowledgments

- Built for Final Year Project
- Powered by Google Gemini AI
- Deployed on Vercel

---

## 📞 Support

For issues and questions, please create an issue in this repository.
