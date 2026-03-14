-- ============================================
-- PASSWORD RESET TOKENS TABLE
-- Add this to your Supabase SQL Editor
-- ============================================

-- Create password_reset_tokens table
CREATE TABLE IF NOT EXISTS password_reset_tokens (
    id INTEGER PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    email VARCHAR(255) NOT NULL,
    token VARCHAR(255) NOT NULL UNIQUE,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    used BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_email ON password_reset_tokens(email);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_token ON password_reset_tokens(token);
CREATE INDEX IF NOT EXISTS idx_password_reset_tokens_expires_at ON password_reset_tokens(expires_at);

-- Add comment
COMMENT ON TABLE password_reset_tokens IS 'Password reset tokens for forgot password functionality';
COMMENT ON COLUMN password_reset_tokens.token IS 'Secure random token sent via email';
COMMENT ON COLUMN password_reset_tokens.expires_at IS 'Token expiration time (1 hour from creation)';
COMMENT ON COLUMN password_reset_tokens.used IS 'Whether token has been used';

-- Verification query
-- SELECT column_name, data_type, is_nullable 
-- FROM information_schema.columns 
-- WHERE table_name = 'password_reset_tokens' 
-- ORDER BY ordinal_position;
