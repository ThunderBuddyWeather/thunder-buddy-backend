-- Run as postgres superuser
-- Create tables and set up permissions

\c thunderbuddy;

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