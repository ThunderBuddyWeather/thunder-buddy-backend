-- Create application user
CREATE USER thunderbuddy WITH PASSWORD 'localdev';

-- Create application database
CREATE DATABASE thunderbuddy;

-- Connect to the application database
\c thunderbuddy;

-- Create schema and set permissions
CREATE SCHEMA IF NOT EXISTS public;
GRANT ALL ON SCHEMA public TO thunderbuddy;

-- Grant necessary privileges
ALTER DATABASE thunderbuddy OWNER TO thunderbuddy;
GRANT ALL PRIVILEGES ON DATABASE thunderbuddy TO thunderbuddy;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO thunderbuddy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO thunderbuddy;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO thunderbuddy;

-- Enable required extensions (if any)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp"; 