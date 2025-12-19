-- Up Migration

-- Add newsletter_opt_in column to users table
ALTER TABLE users ADD COLUMN IF NOT EXISTS newsletter_opt_in BOOLEAN DEFAULT FALSE;

-- Add provider column to support OAuth providers (for future social auth)
ALTER TABLE users ADD COLUMN IF NOT EXISTS provider TEXT;

-- Make password_hash nullable to support OAuth users
ALTER TABLE users ALTER COLUMN password_hash DROP NOT NULL;

-- Create index on provider for faster queries
CREATE INDEX IF NOT EXISTS idx_users_provider ON users(provider);

-- Down Migration
-- ALTER TABLE users DROP COLUMN IF EXISTS newsletter_opt_in;
-- ALTER TABLE users DROP COLUMN IF EXISTS provider;
-- ALTER TABLE users ALTER COLUMN password_hash SET NOT NULL;
-- DROP INDEX IF EXISTS idx_users_provider;