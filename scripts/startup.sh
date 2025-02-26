#!/bin/bash
# Startup script for Thunder Buddy application
# This script initializes the database and starts the application

# Enable command tracing for debugging
set -x

# Exit on error
set -e

echo "Starting Thunder Buddy application..."
echo "Environment variables:"
echo "DB_HOST: ${DB_HOST:-localhost}"
echo "DB_PORT: ${DB_PORT:-5432}"
echo "DB_NAME: ${DB_NAME:-thunderbuddy}"
echo "DB_USER: ${DB_USER:-thunderbuddy}"
echo "DB_ADMIN_USER: ${DB_ADMIN_USER:-postgres}"

# Wait for database to be available
echo "Waiting for database to be available..."
max_retries=60
counter=0
while ! pg_isready -h ${DB_HOST:-localhost} -p ${DB_PORT:-5432} -U ${DB_ADMIN_USER:-postgres} && [ $counter -lt $max_retries ]; do
    echo "Waiting for database connection... ($counter/$max_retries)"
    sleep 2
    counter=$((counter+1))
done

if [ $counter -eq $max_retries ]; then
    echo "Error: Could not connect to database after $max_retries attempts"
    exit 1
fi

echo "Database is available, initializing..."

# Initialize database user and permissions
echo "Running database initialization script..."
python scripts/init_db_user.py
INIT_RESULT=$?
if [ $INIT_RESULT -ne 0 ]; then
    echo "Error: Database initialization failed with exit code $INIT_RESULT"
    exit 1
fi

echo "Database initialized successfully"

# Test database connection before starting the application
echo "Testing database connection..."
python -c "from scripts.db import test_connection; print(test_connection())"
DB_TEST_RESULT=$?
if [ $DB_TEST_RESULT -ne 0 ]; then
    echo "Error: Database connection test failed with exit code $DB_TEST_RESULT"
    exit 1
fi

# Start the application
echo "Starting Flask application..."
# Use exec to replace the shell process with the Flask app
# This ensures signals are properly passed to the Flask process
exec python main.py 