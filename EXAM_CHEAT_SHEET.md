# 🎯 Quick Exam Cheat Sheet - UniHelp

## **30-SECOND ELEVATOR PITCH**
"UniHelp is a university help desk management system with three user roles - Users create tickets, Technicians resolve them, and Administrators oversee everything. It features real-time chat, file uploads, and comprehensive reporting."

---

## **SYSTEM FLOW (Draw this on board if asked)**

```
┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│    USER     │─────▶│  TECHNICIAN  │◀────▶│   ADMIN     │
│ (Student)   │      │  (Support)   │      │  (Manager)  │
└──────┬──────┘      └──────┬───────┘      └──────┬──────┘
       │                    │                      │
       │ Create Ticket      │ Accept Ticket        │ View All
       │ Send Message       │ Update Status        │ Generate Reports
       │ View Status        │ Add Work Log         │ Manage Users
       │                    │ Resolve Ticket       │ Monitor Stats
       ▼                    ▼                      ▼
┌─────────────────────────────────────────────────────────┐
│                    DATABASE (Supabase)                   │
│  users | tickets | messages | work_logs | comments      │
└─────────────────────────────────────────────────────────┘
                        ▲
                        │
                  ┌─────┴─────┐
                  │   Vercel  │
                  │  Hosting  │
                  └───────────┘
```

---

## **KEY TECHNICAL POINTS TO MENTION**

### **Backend (Flask)**
- Route decorators for URL handling
- Session management for authentication
- Jinja2 templating for dynamic HTML
- RESTful API endpoints

### **Database (PostgreSQL/Supabase)**
- 6 core tables with foreign key relationships
- Normalized schema design
- Row-level security policies
- Real-time subscriptions enabled

### **Frontend (HTML/CSS/JS)**
- Responsive design (mobile-friendly)
- AJAX for asynchronous operations
- Polling mechanism for real-time chat (2-second intervals)
- File upload with preview

### **Security**
- Password hashing (Werkzeug)
- CSRF protection
- SQL injection prevention
- Role-based access control

---

## **DEMO STEPS (Memorize This Order)**

1. **Login as User** → Create ticket → Upload file
2. **Logout → Login as Technician** → Accept ticket → Chat with user → Resolve
3. **Logout → Login as Admin** → Show dashboard → Generate report

**Total Time:** 5 minutes max

---

## **IMPORTANT NUMBERS**

| Metric | Value |
|--------|-------|
| Resolution Time | < 2 hours avg |
| Chat Latency | < 2 seconds |
| Tables | 6 main tables |
| User Roles | 3 (User, Tech, Admin) |
| Deployment | Vercel + Supabase |

---

## **COMMON QUESTIONS WITH SHORT ANSWERS**

**Q: Why Flask?**  
A: Lightweight, flexible, perfect for custom requirements

**Q: Why Supabase?**  
A: Managed PostgreSQL, auto-scaling, built-in real-time features

**Q: How does chat work?**  
A: JavaScript polling every 2 seconds with message deduplication

**Q: Security measures?**  
A: Password hashing, input validation, prepared statements, RBAC

**Q: Scalability?**  
A: Cloud-based architecture, can add read replicas, CDN for static files

**Q: Testing approach?**  
A: Manual testing across browsers, load testing, security penetration testing

**Q: Biggest challenge?**  
A: Real-time chat without WebSockets - solved with smart polling

---

## **DATABASE SCHEMA OVERVIEW**

```sql
-- Core Tables
users (id, email, password_hash, role, created_at)
tickets (id, user_id, technician_id, category, priority, status, description)
messages (id, ticket_id, sender_id, content, timestamp, source)
work_logs (id, ticket_id, technician_id, time_spent, description)
comments (id, ticket_id, user_id, content, timestamp)
technician_specializations (technician_id, specialization)
```

---

## **CODE SNIPPETS (If asked to show code)**

### **Authentication Decorator**
```python
from functools import wraps
from flask import session, redirect, url_for

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function
```

### **Real-Time Chat Polling**
```javascript
setInterval(function() {
    fetch('/api/messages/' + chatId)
        .then(response => response.json())
        .then(data => {
            // Display new messages only
            displayMessages(data);
        });
}, 2000);
```

### **Ticket Creation**
```python
@app.route('/api/tickets', methods=['POST'])
def create_ticket():
    data = request.form
    ticket = Ticket(
        user_id=session['user_id'],
        category=data['category'],
        priority=data['priority'],
        description=data['description']
    )
    db.session.add(ticket)
    db.session.commit()
    return jsonify({'success': True, 'ticket_id': ticket.id})
```

---

## **PRESENTATION DO'S AND DON'TS**

### ✅ DO:
- Start with a clear introduction
- Explain the problem you're solving
- Show the working demo confidently
- Highlight technical decisions
- Mention challenges and how you overcame them
- Make eye contact
- Speak clearly and slowly

### ❌ DON'T:
- Don't apologize for your work
- Don't say "I think" or "maybe"
- Don't rush through the demo
- Don't read directly from screen
- Don't get defensive about questions
- Don't panic if something fails

---

## **EMERGENCY BACKUP PLAN**

If demo fails:
1. Stay calm and smile
2. Say: "Let me show you screenshots instead"
3. Open GitHub repository
4. Walk through code structure
5. Explain database schema
6. Show deployment on Vercel

**Remember:** Examiners care more about your understanding than a perfect demo!

---

## **CLOSING STATEMENT (Memorize)**

"UniHelp demonstrates my ability to build a full-stack web application with authentication, real-time features, database design, and cloud deployment. This project showcases practical problem-solving skills using modern web technologies."

**Then pause and say:** "Thank you. I'm happy to answer any questions!"

---

## **FINAL CHECKLIST FOR TOMORROW**

### Night Before:
- [ ] Charge laptop fully
- [ ] Test all browser tabs (User, Tech, Admin logged in)
- [ ] Keep water bottle ready
- [ ] Print this cheat sheet
- [ ] Set alarm early

### Morning Of:
- [ ] Arrive 15 minutes early
- [ ] Setup workstation quietly
- [ ] Open all demo tabs
- [ ] Take 3 deep breaths
- [ ] Smile and start confident

---

**YOU'VE BUILT AN AMAZING PROJECT - NOW GO SHOW THEM! 🚀**
