#!/bin/bash
# Startup script for Thunder Buddy application
# This script initializes the database and starts the application

# Enable command tracing for debugging
set -x

# Don't exit on error immediately - we want to log what's happening
set +e

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

# Check if the database module can be imported
echo "Testing database module import..."
python -c "from scripts.db import test_connection" 2>&1
IMPORT_RESULT=$?
if [ $IMPORT_RESULT -ne 0 ]; then
    echo "Error: Failed to import database module with exit code $IMPORT_RESULT"
    # List the scripts directory to verify files exist
    echo "Contents of scripts directory:"
    ls -la scripts/
    exit 1
fi

# Test database connection before starting the application
echo "Testing database connection..."
python -c "from scripts.db import test_connection; print(test_connection())" 2>&1
DB_TEST_RESULT=$?
if [ $DB_TEST_RESULT -ne 0 ]; then
    echo "Error: Database connection test failed with exit code $DB_TEST_RESULT"
    exit 1
fi

# Check if Flask can be imported
echo "Testing Flask import..."
python -c "from flask import Flask" 2>&1
FLASK_IMPORT_RESULT=$?
if [ $FLASK_IMPORT_RESULT -ne 0 ]; then
    echo "Error: Failed to import Flask with exit code $FLASK_IMPORT_RESULT"
    # Check if Flask is installed
    echo "Checking installed packages:"
    pip list | grep Flask
    exit 1
fi

# Check if main.py exists
echo "Checking if main.py exists..."
if [ ! -f main.py ]; then
    echo "Error: main.py not found"
    echo "Contents of current directory:"
    ls -la
    exit 1
fi

# Try to run main.py with a timeout to catch any startup errors
echo "Testing main.py startup..."
timeout 5 python -c "import main" 2>&1
MAIN_IMPORT_RESULT=$?
if [ $MAIN_IMPORT_RESULT -ne 0 ] && [ $MAIN_IMPORT_RESULT -ne 124 ]; then
    echo "Error: Failed to import main.py with exit code $MAIN_IMPORT_RESULT"
    exit 1
fi

# Start the application
echo "Starting Flask application..."
# Use exec to replace the shell process with the Flask app
# This ensures signals are properly passed to the Flask process
exec python main.py 2>&1 