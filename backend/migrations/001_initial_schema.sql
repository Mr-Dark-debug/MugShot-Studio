-- Up Migration

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    email_confirmed BOOLEAN DEFAULT FALSE,
    password_hash TEXT,
    username TEXT UNIQUE NOT NULL,
    full_name TEXT,
    dob DATE,
    profile_photo_asset_id UUID,
    plan TEXT DEFAULT 'free',
    credits INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);
CREATE INDEX IF NOT EXISTS idx_users_username ON users(username);

-- Assets table
CREATE TYPE asset_type AS ENUM ('selfie', 'ref', 'copy_target', 'render', 'profile_photo');
CREATE TABLE IF NOT EXISTS assets (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    type asset_type NOT NULL,
    storage_path TEXT NOT NULL,
    width INTEGER,
    height INTEGER,
    md5 TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Circular dependency fix: Add FK to users after assets table exists
ALTER TABLE users ADD CONSTRAINT fk_users_profile_photo FOREIGN KEY (profile_photo_asset_id) REFERENCES assets(id);

-- Projects table
CREATE TYPE project_mode AS ENUM ('design', 'copy');
CREATE TYPE project_status AS ENUM ('draft', 'queued', 'running', 'done', 'failed');
CREATE TABLE IF NOT EXISTS projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    mode project_mode NOT NULL,
    platform TEXT,
    width INTEGER,
    height INTEGER,
    status project_status DEFAULT 'draft',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Prompts table
CREATE TABLE IF NOT EXISTS prompts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    raw_jsonb JSONB,
    normalized_jsonb JSONB,
    seed INTEGER,
    model_pref TEXT
);

-- Jobs table
CREATE TYPE job_quality AS ENUM ('draft', 'std', '4k');
CREATE TYPE job_status AS ENUM ('queued', 'running', 'succeeded', 'failed');
CREATE TABLE IF NOT EXISTS jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id),
    model TEXT,
    quality job_quality DEFAULT 'std',
    status job_status DEFAULT 'queued',
    cost_credits INTEGER,
    provider_meta JSONB,
    started_at TIMESTAMPTZ,
    finished_at TIMESTAMPTZ
);

-- Renders table
CREATE TABLE IF NOT EXISTS renders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    job_id UUID REFERENCES jobs(id),
    asset_id UUID REFERENCES assets(id),
    variant INTEGER,
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Chats table
CREATE TABLE IF NOT EXISTS chats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    session_name TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Messages table
CREATE TYPE message_sender AS ENUM ('user', 'system', 'ai');
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    chat_id UUID REFERENCES chats(id),
    sender message_sender NOT NULL,
    content TEXT, -- or JSONB if needed
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Audit table
CREATE TABLE IF NOT EXISTS audit (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    action TEXT,
    delta_credits INTEGER,
    meta JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Down Migration
-- DROP TABLE IF EXISTS audit;
-- DROP TABLE IF EXISTS messages;
-- DROP TABLE IF EXISTS chats;
-- DROP TABLE IF EXISTS renders;
-- DROP TABLE IF EXISTS jobs;
-- DROP TABLE IF EXISTS prompts;
-- DROP TABLE IF EXISTS projects;
-- ALTER TABLE users DROP CONSTRAINT fk_users_profile_photo;
-- DROP TABLE IF EXISTS assets;
-- DROP TABLE IF EXISTS users;
-- DROP TYPE IF EXISTS message_sender;
-- DROP TYPE IF EXISTS job_status;
-- DROP TYPE IF EXISTS job_quality;
-- DROP TYPE IF EXISTS project_status;
-- DROP TYPE IF EXISTS project_mode;
-- DROP TYPE IF EXISTS asset_type;