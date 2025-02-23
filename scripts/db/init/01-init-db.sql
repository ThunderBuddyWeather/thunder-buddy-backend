-- Run as postgres superuser
-- Initial setup and user creation

-- Create application database
CREATE DATABASE thunderbuddy;

-- Create application user with limited privileges
CREATE USER thunderbuddy WITH PASSWORD '${DB_PASSWORD}';

-- Connect to the application database
\c thunderbuddy;

-- Create extensions (requires superuser)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create schema
CREATE SCHEMA IF NOT EXISTS public;

-- Revoke all permissions from PUBLIC for security
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;

-- Grant minimal required privileges to application user
GRANT CONNECT ON DATABASE thunderbuddy TO thunderbuddy;
GRANT USAGE ON SCHEMA public TO thunderbuddy;
GRANT USAGE ON EXTENSION uuid-ossp TO thunderbuddy;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO thunderbuddy;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO thunderbuddy; 