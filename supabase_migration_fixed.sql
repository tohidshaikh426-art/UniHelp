-- Supabase Database Schema for UniHelp (FIXED VERSION)
-- Run this in Supabase SQL Editor
-- This version fixes the "user" reserved keyword issue

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create User Table (using quoted identifier)
CREATE TABLE "user" (
    userid SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    passwordhash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL CHECK(role IN ('admin', 'staff', 'technician', 'student')),
    isapproved BOOLEAN DEFAULT false,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Ticket Table
CREATE TABLE ticket (
    ticketid SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    category VARCHAR(50) NOT NULL,
    priority VARCHAR(20) DEFAULT 'Medium' CHECK(priority IN ('Low', 'Medium', 'High', 'Urgent')),
    status VARCHAR(30) DEFAULT 'Open' CHECK(status IN ('Open', 'In Progress', 'Pending', 'Resolved', 'Closed', 'Reopened')),
    filepath VARCHAR(255),
    createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updatedat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolvedat TIMESTAMP,
    userid INTEGER NOT NULL REFERENCES "user"(userid) ON DELETE CASCADE,
    assignedto INTEGER REFERENCES "user"(userid) ON DELETE SET NULL,
    resolvedby INTEGER REFERENCES "user"(userid) ON DELETE SET NULL,
    time_spent_hours REAL DEFAULT 0,
    resolution_notes TEXT,
    satisfaction_rating INTEGER CHECK(satisfaction_rating >= 1 AND satisfaction_rating <= 5)
);

-- Create Comment Table
CREATE TABLE comment (
    commentid SERIAL PRIMARY KEY,
    content TEXT NOT NULL,
    createdat TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ticketid INTEGER NOT NULL REFERENCES ticket(ticketid) ON DELETE CASCADE,
    userid INTEGER NOT NULL REFERENCES "user"(userid) ON DELETE CASCADE
);

-- Create Chat Session Table
CREATE TABLE chat_session (
    sessionid SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL REFERENCES "user"(userid) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP,
    escalated_ticket_id INTEGER REFERENCES ticket(ticketid) ON DELETE SET NULL
);

-- Create Chat Message Table
CREATE TABLE chat_message (
    messageid SERIAL PRIMARY KEY,
    sessionid INTEGER NOT NULL REFERENCES chat_session(sessionid) ON DELETE CASCADE,
    sender VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Chatbot Interaction Table
CREATE TABLE chatbot_interaction (
    chatid SERIAL PRIMARY KEY,
    userid INTEGER NOT NULL REFERENCES "user"(userid) ON DELETE CASCADE,
    query TEXT NOT NULL,
    response TEXT NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create User Presence Table
CREATE TABLE user_presence (
    userid INTEGER PRIMARY KEY REFERENCES "user"(userid) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'offline',
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Live Chat Table
CREATE TABLE live_chat (
    livechatid SERIAL PRIMARY KEY,
    sessionid INTEGER NOT NULL REFERENCES chat_session(sessionid) ON DELETE CASCADE,
    technicianid INTEGER NOT NULL REFERENCES "user"(userid) ON DELETE CASCADE,
    status VARCHAR(20) DEFAULT 'active',
    started_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    ended_at TIMESTAMP
);

-- Create Technician Work Log Table
CREATE TABLE technician_work_log (
    worklogid SERIAL PRIMARY KEY,
    technicianid INTEGER NOT NULL REFERENCES "user"(userid) ON DELETE CASCADE,
    ticketid INTEGER REFERENCES ticket(ticketid) ON DELETE SET NULL,
    work_type VARCHAR(50) NOT NULL CHECK(work_type IN ('ticket_resolution', 'live_chat', 'maintenance', 'other')),
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP,
    hours_worked REAL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Ticket History Table
CREATE TABLE ticket_history (
    historyid SERIAL PRIMARY KEY,
    ticketid INTEGER NOT NULL REFERENCES ticket(ticketid) ON DELETE CASCADE,
    changed_by INTEGER NOT NULL REFERENCES "user"(userid) ON DELETE CASCADE,
    old_status VARCHAR(30),
    new_status VARCHAR(30) NOT NULL,
    old_assignedto INTEGER REFERENCES "user"(userid) ON DELETE SET NULL,
    new_assignedto INTEGER REFERENCES "user"(userid) ON DELETE SET NULL,
    change_reason TEXT,
    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create Monthly Reports Cache Table
CREATE TABLE monthly_reports_cache (
    reportid SERIAL PRIMARY KEY,
    report_month VARCHAR(7) NOT NULL, -- Format: YYYY-MM
    report_type VARCHAR(50) NOT NULL,
    report_data JSONB NOT NULL, -- Changed from TEXT to JSONB for PostgreSQL
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(report_month, report_type)
);

-- Create Indexes for Better Performance (FIXED: quoted "user" table)
CREATE INDEX idx_ticket_status ON ticket(status);
CREATE INDEX idx_ticket_userid ON ticket(userid);
CREATE INDEX idx_ticket_assignedto ON ticket(assignedto);
CREATE INDEX idx_user_email ON "user"(email);
CREATE INDEX idx_user_role ON "user"(role);
CREATE INDEX idx_comment_ticketid ON comment(ticketid);
CREATE INDEX idx_chat_session_userid ON chat_session(userid);
CREATE INDEX idx_ticket_history_ticketid ON ticket_history(ticketid);

-- Insert Default Admin User
INSERT INTO "user" (name, email, passwordhash, role, isapproved) 
VALUES (
    'Admin User', 
    'admin@unihelp.com', 
    'scrypt:32768:8:1$YOUR_HASHED_PASSWORD_HERE', -- Replace with actual hash
    'admin', 
    true
);

-- Insert Sample Technician
INSERT INTO "user" (name, email, passwordhash, role, isapproved) 
VALUES (
    'John Tech', 
    'tech@unihelp.com', 
    'scrypt:32768:8:1$YOUR_HASHED_PASSWORD_HERE', 
    'technician', 
    true
);

-- Insert Sample Staff
INSERT INTO "user" (name, email, passwordhash, role, isapproved) 
VALUES (
    'Mary Staff', 
    'staff@unihelp.com', 
    'scrypt:32768:8:1$YOUR_HASHED_PASSWORD_HERE', 
    'staff', 
    true
);

-- Insert Sample Student
INSERT INTO "user" (name, email, passwordhash, role, isapproved) 
VALUES (
    'Alice Student', 
    'student@unihelp.com', 
    'scrypt:32768:8:1$YOUR_HASHED_PASSWORD_HERE', 
    'student', 
    true
);
