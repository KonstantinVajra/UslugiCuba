-- Creates the initial schema and tables required for the application.
-- This script is designed to fix the "relation svc.vehicle does not exist" error
-- by creating the necessary tables from scratch.

-- 1. Create the schema for our service
CREATE SCHEMA IF NOT EXISTS svc;

-- 2. Create the user table to store all bot users
CREATE TABLE IF NOT EXISTS svc."user" (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(255),
    role VARCHAR(20) NOT NULL DEFAULT 'client', -- Roles: client, provider, admin
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE svc."user" IS 'Stores all users interacting with the bot.';

-- 3. Create the provider table for users who offer services
CREATE TABLE IF NOT EXISTS svc.provider (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL UNIQUE REFERENCES svc."user"(id) ON DELETE CASCADE,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(50),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE svc.provider IS 'Stores service provider specific information.';

-- 4. Create the vehicle table for cars offered by providers
CREATE TABLE IF NOT EXISTS svc.vehicle (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES svc.provider(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    photo_file_ids TEXT[] NOT NULL, -- Array of Telegram file_ids
    seats INTEGER,
    price_per_hour NUMERIC(10, 2),
    price_details TEXT,
    status VARCHAR(20) NOT NULL DEFAULT 'draft', -- Status: draft, published, archived
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
COMMENT ON TABLE svc.vehicle IS 'Stores vehicle information for providers.';

-- Add an index on vehicle status for faster lookups
CREATE INDEX IF NOT EXISTS idx_vehicle_status ON svc.vehicle(status);