-- ============================================
-- SUPABASE MIGRATION SCRIPT
-- Fix chat_session table to use auto-incrementing integer sessionid
-- ============================================

-- This script fixes the chat_session table schema
-- Run this in your Supabase SQL Editor: https://app.supabase.com/project/_/sql

-- Step 1: Drop existing chat_session table (if it exists with wrong schema)
DROP TABLE IF EXISTS chat_message CASCADE;
DROP TABLE IF EXISTS chat_session CASCADE;

-- Step 2: Recreate chat_session table with proper auto-increment
CREATE TABLE IF NOT EXISTS chat_session (
    sessionid INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    userid INTEGER NOT NULL REFERENCES "user"(userid),
    status VARCHAR(20) DEFAULT 'active',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE,
    escalated_ticket_id INTEGER REFERENCES ticket(ticketid)
);

-- Step 3: Recreate chat_message table
CREATE TABLE IF NOT EXISTS chat_message (
    messageid INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    sessionid INTEGER NOT NULL REFERENCES chat_session(sessionid),
    sender VARCHAR(20) NOT NULL,
    message TEXT NOT NULL,
    intent VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Step 4: Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_chat_session_userid ON chat_session(userid);
CREATE INDEX IF NOT EXISTS idx_chat_session_status ON chat_session(status);
CREATE INDEX IF NOT EXISTS idx_chat_message_sessionid ON chat_message(sessionid);
CREATE INDEX IF NOT EXISTS idx_chat_message_createdat ON chat_message(created_at);

-- Step 5: Add comments for documentation
COMMENT ON TABLE chat_session IS 'AI chatbot conversation sessions';
COMMENT ON COLUMN chat_session.sessionid IS 'Auto-incrementing session ID';
COMMENT ON COLUMN chat_session.userid IS 'User who started the chat session';
COMMENT ON COLUMN chat_session.status IS 'Session status: active/resolved/escalated';

COMMENT ON TABLE chat_message IS 'Individual messages within chat sessions';
COMMENT ON COLUMN chat_message.sessionid IS 'Reference to parent chat session';
COMMENT ON COLUMN chat_message.sender IS 'Message sender: user/ai/technician';
COMMENT ON COLUMN chat_message.intent IS 'AI-detected intent or classification';

-- ============================================
-- VERIFICATION QUERIES
-- Run these to verify the fix worked
-- ============================================

-- Check table structure
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'chat_session' 
-- ORDER BY ordinal_position;

-- Check if identity column is set up correctly
-- SELECT column_name, identity_generation 
-- FROM information_schema.columns 
-- WHERE table_name = 'chat_session' AND column_name = 'sessionid';

-- ============================================
-- USAGE NOTES
-- ============================================
-- 
-- After running this migration:
-- 1. The chat_session.sessionid will auto-generate as INTEGER
-- 2. When inserting, DO NOT provide sessionid value
-- 3. After insert, get the generated ID from response.data[0]['sessionid']
-- 
-- Example Supabase insert (from app.py):
--   response = db.client.table('chat_session').insert({
--       'userid': user_id,
--       'status': 'active'
--   }).execute()
--   
--   session_id = response.data[0]['sessionid']  # Auto-generated integer
-- ============================================
