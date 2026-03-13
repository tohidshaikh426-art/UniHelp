# 🏗️ UniHelp System Architecture Overview

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE LAYER                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │   Admin  │  │Technician│  │   Staff  │  │ Student  │        │
│  │ Dashboard│  │ Dashboard│  │ Dashboard│  │ Dashboard│        │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘  └────┬─────┘        │
└───────┼─────────────┼─────────────┼─────────────┼───────────────┘
        │             │             │             │
        └─────────────┴──────┬──────┴─────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                    FLASK APPLICATION LAYER                       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Route Handlers & Controllers                 │  │
│  │  • Authentication (login/logout/register)                │  │
│  │  • Ticket Management (CRUD operations)                   │  │
│  │  • User Management (admin functions)                     │  │
│  │  • Chat Integration (AI + live chat)                     │  │
│  │  • Reporting & Analytics                                 │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              Business Logic Layer                         │  │
│  │  • Role-based Access Control (RBAC)                      │  │
│  │  • Ticket Workflow Management                            │  │
│  │  • Email Notifications                                   │  │
│  │  • File Upload Handling                                  │  │
│  │  • AI Chatbot Integration                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼────────┐  ┌───────▼────────┐  ┌───────▼────────┐
│  AUTHENTICATION│  │  FILE STORAGE  │  │  AI SERVICE    │
│     LAYER      │  │     LAYER      │  │     LAYER      │
│  • Sessions    │  │  • Uploads/    │  │  • Google      │
│  • Password    │  │    attachments │  │    Gemini AI   │
│    Hashing     │  │  • 16MB limit  │  │  • Intent      │
│  • Role-based  │  │  • Secure      │  │    Detection   │
│    Access      │  │    filenames   │  │  • Auto-       │
│                │  │                │  │    responses   │
└────────────────┘  └────────────────┘  └────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                      DATA ACCESS LAYER                           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              SQLite Database Connection                   │  │
│  │  • Connection pooling                                    │  │
│  │  • Query execution                                       │  │
│  │  • Transaction management                                │  │
│  │  • Error handling                                        │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
┌────────────────────────────▼────────────────────────────────────┐
│                       DATABASE LAYER                             │
│                                                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │    USER      │  │    TICKET    │  │   COMMENT    │         │
│  │  - userid PK │  │ - ticketid PK│  │ - commentidPK│         │
│  │  - name      │  │  - title     │  │  - content   │         │
│  │  - email     │  │  - description│ │  - createdat │         │
│  │  - password  │  │  - status    │  │  - ticketidFK│         │
│  │  - role      │  │  - priority  │  │  - userid FK │         │
│  │  - isapproved│  │  - userid FK │  │              │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │ CHAT_SESSION │  │ CHAT_MESSAGE │  │  LIVE_CHAT   │         │
│  │ - sessionid  │  │ - messageid  │  │ - livechatid │         │
│  │ - userid FK  │  │ - sessionidFK│  │ - sessionidFK│         │
│  │ - status     │  │ - sender     │  │ - technician │          │
│  │ - created_at │  │ - message    │  │ - status     │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │TECH_WORK_LOG │  │TICKET_HISTORY│  │MONTHLY_REPORT│         │
│  │ - worklogid  │  │ - historyid  │  │ - reportid   │         │
│  │ - technician │  │ - ticketidFK │  │ - month      │         │
│  │ - ticketidFK │  │ - old_status │  │ - type       │         │
│  │ - hours      │  │ - new_status │  │ - data (JSON)│         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
│                                                                 │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │        Additional Tables: user_presence,                 │  │
│  │        chatbot_interaction                               │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Diagrams

### 1. **Ticket Creation Flow**

```
User (Staff/Student)
    │
    ├─► Create Ticket Form
    │      ├─ Title
    │      ├─ Description
    │      ├─ Category
    │      └─ Priority
    │
    ├─► Upload Attachment (optional)
    │
    ├─► Flask Route: /ticket/create
    │      ├─ Validate input
    │      ├─ Save file (if any)
    │      └─ Insert into ticket table
    │
    ├─► Create Ticket History Entry
    │      └─ Log: "Ticket created - Status: Open"
    │
    ├─► Send Notification Email
    │      └─ To: admin & assigned technician
    │
    └─► Redirect to Ticket View
           └─ Flash: "Ticket created successfully!"
```

---

### 2. **Ticket Assignment Flow**

```
Admin Dashboard
    │
    ├─► View All Open Tickets
    │
    ├─► Select Technician
    │      └─ Based on:
    │         ├─ Availability
    │         ├─ Expertise
    │         └─ Workload
    │
    ├─► Update Ticket
    │      ├─ assignedto = technician_id
    │      └─ status = "In Progress"
    │
    ├─► Create Ticket History Entry
    │      ├─ old_status = "Open"
    │      ├─ new_status = "In Progress"
    │      └─ changed_by = admin_id
    │
    └─► Notify Technician
           └─ Email: "New ticket assigned"
```

---

### 3. **Ticket Resolution Flow**

```
Technician Dashboard
    │
    ├─► View Assigned Tickets
    │
    ├─► Work on Ticket
    │      ├─ Update status
    │      ├─ Add comments
    │      └─ Log work hours
    │
    ├─► Resolve Ticket
    │      ├─ status = "Resolved"
    │      ├─ resolution_notes = "..."
    │      ├─ resolvedat = NOW()
    │      └─ resolvedby = technician_id
    │
    ├─► Create Work Log Entry
    │      ├─ work_type = "ticket_resolution"
    │      ├─ hours_worked = calculated
    │      └─ description = "..."
    │
    ├─► Create Ticket History Entry
    │      └─ Log status change to "Resolved"
    │
    └─► Notify User
           └─ Email: "Your ticket has been resolved"
                └─ Include satisfaction rating link
```

---

### 4. **AI Chatbot Flow**

```
User Question
    │
    ├─► Chat Interface
    │
    ├─► Create Chat Session
    │      └─ sessionid generated
    │
    ├─► Send to Google Gemini AI
    │      ├─ Context: IT support knowledge base
    │      └─ Query: User's question
    │
    ├─► Receive AI Response
    │      ├─ Parse response
    │      └─ Detect intent
    │
    ├─► Store in chat_message
    │      ├─ sessionid
    │      ├─ sender = "ai"
    │      ├─ message = AI response
    │      └─ intent = detected_intent
    │
    ├─► Evaluate if Escalation Needed
    │      ├─ If unresolved → Create ticket
    │      └─ If complex → Connect live technician
    │
    └─► Display Response to User
```

---

## Security Architecture

### Authentication Flow

```
Login Request
    │
    ├─► Validate Credentials
    │      └─ Check email exists
    │
    ├─► Verify Password
    │      └─ check_password_hash(
    │           input_password,
    │           stored_hash
    │         )
    │
    ├─► Check Approval Status
    │      └─ isapproved = True?
    │
    ├─► Create Session
    │      ├─ session['user_id'] = user_id
    │      ├─ session['role'] = role
    │      └─ session['email'] = email
    │
    └─► Update User Presence
           └─ status = "online"
```

---

### Authorization Matrix

```
┌─────────────────┬──────┬──────┬──────┬────────┐
│ Feature         │ Admin│ Tech │ Staff│Student│
├─────────────────┼──────┼──────┼──────┼────────┤
│ View All Tickets│  ✓   │  ✗   │  ✗   │   ✗    │
│ Create Ticket   │  ✓   │  ✓   │  ✓   │   ✓    │
│ Assign Tickets  │  ✓   │  ✗   │  ✗   │   ✗    │
│ Resolve Tickets │  ✓   │  ✓   │  ✗   │   ✗    │
│ Rate Ticket     │  ✗   │  ✗   │  ✓   │   ✓    │
│ User Management │  ✓   │  ✗   │  ✗   │   ✗    │
│ View Reports    │  ✓   │  ✗   │  ✗   │   ✗    │
│ Live Chat       │  ✓   │  ✓   │  ✓   │   ✓    │
│ AI Chatbot      │  ✓   │  ✓   │  ✓   │   ✓    │
└─────────────────┴──────┴──────┴──────┴────────┘
```

---

## Deployment Architecture (Vercel)

```
┌─────────────────────────────────────────────────────────┐
│                    Internet/Users                        │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
        ┌────────────────────┐
        │   Vercel Edge      │
        │   Network/CDN      │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  Vercel Serverless │
        │     Functions      │
        │  ┌──────────────┐  │
        │  │ app.py routes│  │
        │  │ Each route = │  │
        │  │ serverless   │  │
        │  │ function     │  │
        │  └──────────────┘  │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │  Application Code  │
        │  ├─ Flask logic    │
        │  ├─ DB queries     │
        │  ├─ File handling  │
        │  └─ AI integration │
        └────────┬───────────┘
                 │
                 ▼
        ┌────────────────────┐
        │   SQLite Database  │
        │   (unihelp.db)     │
        │   Stored on:       │
        │   - Vercel Blob    │
        │   - Or external    │
        └────────────────────┘
```

---

## Technology Stack Summary

### Backend
- **Language:** Python 3.10+
- **Framework:** Flask 2.3.3
- **Database:** SQLite3 (built-in)
- **Security:** Werkzeug password hashing
- **File Upload:** Werkzeug secure_filename
- **Environment:** python-dotenv

### Frontend
- **Templates:** Jinja2 (Flask templating)
- **CSS:** Custom CSS + Bootstrap
- **JavaScript:** Vanilla JS for interactivity
- **Charts:** Chart.js (for dashboards)

### AI Integration
- **Provider:** Google Gemini API
- **Model:** gemini-1.5-pro
- **Library:** google-generativeai==0.3.2

### Email
- **Library:** Flask-Mail 0.9.1
- **Protocol:** SMTP
- **Features:** HTML emails, attachments

### Deployment
- **Platform:** Vercel (Serverless)
- **WSGI Server:** Vercel built-in
- **Environment:** Serverless functions

---

## Performance Optimizations

1. **Database Indexes**
   - Primary keys auto-indexed
   - Foreign keys indexed for joins
   - Timestamp indexes for reporting

2. **Query Optimization**
   - SELECT only needed columns
   - JOIN instead of subqueries
   - LIMIT for pagination

3. **Caching Strategy**
   - Monthly reports pre-computed
   - Session data cached in memory
   - Static files served via CDN

4. **File Upload**
   - 16MB size limit
   - Secure filename sanitization
   - Virus scanning (recommended)

---

## Scalability Considerations

### Current Capacity (SQLite)
- ✅ Up to 100 concurrent users
- ✅ 10,000+ tickets per year
- ✅ Single server deployment
- ✅ Low to medium traffic

### Future Scaling Path

**Stage 1: Optimize SQLite**
- Add WAL mode for better concurrency
- Implement connection pooling
- Add query caching

**Stage 2: Migrate to PostgreSQL**
- Replace sqlite3 with psycopg2
- Update connection strings
- Migrate data with pg_dump

**Stage 3: Horizontal Scaling**
- Add read replicas
- Implement Redis caching
- Load balancer for multiple instances

---

**This architecture document demonstrates professional system design for your final year project defense!** 🎓✨
