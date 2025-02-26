-- Create the application user with limited privileges
CREATE USER thunderbuddy WITH PASSWORD 'localdev';

-- Create the database owned by thunderbuddy
CREATE DATABASE thunderbuddy OWNER thunderbuddy;

-- Connect to the new database
\c thunderbuddy

-- Grant necessary privileges to thunderbuddy user
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO thunderbuddy;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO thunderbuddy;

-- Set default privileges for future tables and sequences
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO thunderbuddy;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON SEQUENCES TO thunderbuddy; 