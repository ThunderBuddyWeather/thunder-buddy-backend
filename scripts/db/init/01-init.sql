-- Create application user with limited privileges
CREATE USER thunderbuddy WITH PASSWORD '${DB_PASSWORD}';

-- Create application database
CREATE DATABASE thunderbuddy;

-- Connect to the application database
\c thunderbuddy;

-- Create schema
CREATE SCHEMA IF NOT EXISTS public;

-- Create extensions if needed
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Set up proper permissions
-- Revoke all permissions from PUBLIC
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC;

-- Grant specific permissions to application user
GRANT CONNECT ON DATABASE thunderbuddy TO thunderbuddy;
GRANT USAGE ON SCHEMA public TO thunderbuddy;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO thunderbuddy;
GRANT USAGE ON ALL SEQUENCES IN SCHEMA public TO thunderbuddy;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO thunderbuddy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public
    GRANT USAGE ON SEQUENCES TO thunderbuddy;

-- Create any required tables here
CREATE TABLE IF NOT EXISTS weather_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zip_code VARCHAR(10) NOT NULL,
    country_code CHAR(2) NOT NULL,
    temperature DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Grant permissions on existing tables
GRANT SELECT, INSERT, UPDATE, DELETE ON weather_data TO thunderbuddy;

-- Set ownership of the schema and objects
ALTER SCHEMA public OWNER TO thunderbuddy;
ALTER TABLE weather_data OWNER TO thunderbuddy; 