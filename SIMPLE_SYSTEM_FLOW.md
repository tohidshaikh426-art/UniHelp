# 📊 UniHelp System Flow - Simple PPT Version

---

## **FLOW 1: COMPLETE TICKET LIFECYCLE**

```
User Login → Create Ticket → Admin Assigns Technician 
→ Technician Resolves → User Confirms → END
```

### **Steps:**
1. **User Login** - Student/staff logs in
2. **Create Ticket** - Fill form with issue details
3. **Admin Assigns** - Admin assigns to available technician
4. **Technician Works** - Tech accepts and resolves issue
5. **User Confirms** - User verifies solution
6. **END** - Ticket closed

---

## **FLOW 2: LIVE CHAT PROCESS**

```
User Requests Chat → Technician Accepts → Real-time Messaging 
→ Problem Solved → End Chat → Save Transcript
```

### **Steps:**
1. **User Requests** - Click chat button
2. **Technician Accepts** - Notification received
3. **Messaging** - Exchange messages (every 2 sec polling)
4. **Problem Solved** - Issue resolved via chat
5. **End Chat** - Either party ends session
6. **Save** - Chat history stored in database

---

## **FLOW 3: USER REGISTRATION**

```
Visit Register Page → Fill Form → Validate → Create Account 
→ Auto-Login → Dashboard
```

### **Steps:**
1. **Visit Page** - Click register link
2. **Fill Form** - Name, email, password, role
3. **Validate** - Check email format, password strength
4. **Create Account** - Save to database with hashed password
5. **Auto-Login** - Session created
6. **Dashboard** - Redirected to user dashboard

---

## **FLOW 4: PASSWORD RESET**

```
Forgot Password → Enter Email → Send Reset Link 
→ Click Link → New Password → Login
```

### **Steps:**
1. **Request** - Click "Forgot Password"
2. **Enter Email** - Submit university email
3. **Send Token** - Email with reset link sent
4. **Click Link** - User opens email link
5. **New Password** - Enter and confirm new password
6. **Login** - Auto-login or redirect to login page

---

## **FLOW 5: ADMIN REPORTING**

```
Admin Login → Select Report Type → Choose Date Range 
→ Generate Report → View/Export → END
```

### **Steps:**
1. **Admin Login** - Administrator accesses dashboard
2. **Select Type** - Monthly or custom report
3. **Choose Dates** - Pick month or date range
4. **Generate** - System queries database
5. **View/Export** - Display charts or download PDF/Excel
6. **END** - Report complete

---

## **FLOW 6: TECHNICIAN WORKFLOW**

```
Tech Login → View Assigned Tickets → Accept Ticket 
→ Work on Issue → Update Status → Resolve → Notify User
```

### **Steps:**
1. **Tech Login** - Technician accesses dashboard
2. **View Queue** - See assigned tickets
3. **Accept** - Click accept on new ticket
4. **Work** - Troubleshoot and add work logs
5. **Update** - Change status to "In Progress"
6. **Resolve** - Mark as resolved with solution notes
7. **Notify** - Email sent to user

---

## **SIMPLIFIED SYSTEM ARCHITECTURE**

```
┌─────────────┐
│    USERS    │ (Students/Staff)
└──────┬──────┘
       │ Create Tickets
       │ Send Messages
       ▼
┌─────────────┐      ┌──────────────┐
│   FLASK     │◀────▶│   SUPABASE   │
│  (Backend)  │      │ (Database)   │
└──────┬──────┘      └──────────────┘
       │
       ├──────► Technicians (Resolve tickets)
       │
       └──────► Admins (Manage & Reports)
```

---

## **DATA FLOW DIAGRAM**

```
User Input → Flask Routes → Database Operations → Response
     ▲                                              │
     │                                              ▼
     └─────────── Frontend (HTML/CSS/JS) ◀──────────┘
```

---

## **KEY PROCESSES IN ONE LINE EACH:**

✅ **Registration:** Fill form → Validate → Hash password → Save to DB  
✅ **Login:** Enter credentials → Verify hash → Create session → Dashboard  
✅ **Create Ticket:** Fill form → Save to DB → Notify admin  
✅ **Assign Ticket:** Admin selects tech → Update DB → Notify both  
✅ **Resolve Ticket:** Tech works → Add notes → Mark resolved → Email user  
✅ **Live Chat:** Poll every 2s → Fetch messages → Display → Store  
✅ **Reports:** Query DB → Aggregate data → Generate charts → Export  

---

## **FOR YOUR PPT SLIDES:**

### **Slide 1: User Creates Ticket**
```
START → Login → Create Ticket Form → Submit → Saved to DB → END
```

### **Slide 2: Ticket Assignment**
```
Admin Views Unassigned → Selects Technician → Updates DB → 
Technician Notified → Accepts → STARTS WORK
```

### **Slide 3: Resolution Process**
```
Technician Works → Adds Work Log → Marks Resolved → 
User Notified → Confirms → Ticket CLOSED
```

### **Slide 4: Real-Time Chat**
```
Initiate Chat → Accept → Message Loop (Poll every 2s) → 
Exchange Messages → End Chat → Save History
```

### **Slide 5: Admin Oversight**
```
Login → View Dashboard → Select Report → Generate Stats → 
Export PDF/Excel → END
```

---

## **30-SECOND EXPLANATION SCRIPT:**

*"The system starts when a user creates a ticket. The admin assigns it to an available technician who then resolves the issue. Users can also chat in real-time with technicians for immediate help. Administrators can generate reports and monitor the entire system. All data is stored securely in the cloud using Supabase."*

---

**Perfect for PPT slides! Copy-paste ready! 📊**
