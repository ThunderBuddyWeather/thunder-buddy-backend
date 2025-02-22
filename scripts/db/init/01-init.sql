-- Create user and database
CREATE USER thunderbuddy WITH PASSWORD 'localdev';
ALTER USER thunderbuddy WITH SUPERUSER;
CREATE DATABASE thunderbuddy OWNER thunderbuddy;
GRANT ALL PRIVILEGES ON DATABASE thunderbuddy TO thunderbuddy;

-- Connect to the thunderbuddy database
\c thunderbuddy;

-- Create extensions and schemas if needed
CREATE SCHEMA IF NOT EXISTS public;
GRANT ALL ON SCHEMA public TO thunderbuddy; 