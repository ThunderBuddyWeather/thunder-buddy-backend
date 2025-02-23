-- Run as postgres superuser
-- Initial setup and user creation

-- Create application user with limited privileges
CREATE USER thunderbuddy WITH PASSWORD 'localdev';

-- Create application database
CREATE DATABASE thunderbuddy;

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

-- Grant usage on uuid-ossp functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO thunderbuddy;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA pg_catalog TO thunderbuddy;
GRANT EXECUTE ON FUNCTION uuid_generate_v4() TO thunderbuddy;

-- Create weather_data table
CREATE TABLE IF NOT EXISTS public.weather_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    zip_code VARCHAR(10) NOT NULL,
    country_code CHAR(2) NOT NULL,
    temperature DECIMAL(5,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create index for common queries
CREATE INDEX IF NOT EXISTS idx_weather_data_zip_country 
ON public.weather_data(zip_code, country_code);

-- Create trigger for updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_weather_data_updated_at
    BEFORE UPDATE ON public.weather_data
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Grant specific permissions to application user
GRANT SELECT, INSERT, UPDATE, DELETE ON public.weather_data TO thunderbuddy;
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO thunderbuddy;

-- Create versioning table for migrations
CREATE TABLE IF NOT EXISTS public.schema_versions (
    version INTEGER PRIMARY KEY,
    description TEXT NOT NULL,
    applied_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    applied_by TEXT DEFAULT CURRENT_USER
);

-- Grant read-only access to schema_versions
GRANT SELECT ON public.schema_versions TO thunderbuddy;

-- Record initial schema version
INSERT INTO public.schema_versions (version, description)
VALUES (1, 'Initial schema setup') ON CONFLICT DO NOTHING;

-- Set default privileges for future objects
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO thunderbuddy;
ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public
    GRANT USAGE, SELECT ON SEQUENCES TO thunderbuddy;

-- Make sure the application user can access the database
ALTER DATABASE thunderbuddy OWNER TO thunderbuddy; 