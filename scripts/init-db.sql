-- Development database initialization
-- This script sets up the development database with some initial configuration

-- Create development database if it doesn't exist
-- (This is handled by Docker, but included for reference)

-- Create extensions that might be useful for development
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Insert some sample data for development (optional)
-- This will be created by the application, but can be useful for testing

-- Create a sample user for testing (if you add user management later)
-- INSERT INTO users (id, username, email) VALUES
-- (uuid_generate_v4(), 'testuser', 'test@example.com')
-- ON CONFLICT DO NOTHING;
