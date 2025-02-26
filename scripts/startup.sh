#!/bin/bash
# Startup script for Thunder Buddy application
# This script initializes the database and starts the application

set -e

echo "Starting Thunder Buddy application..."

# Wait for database to be available
echo "Waiting for database to be available..."
max_retries=30
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
python scripts/init_db_user.py
if [ $? -ne 0 ]; then
    echo "Error: Database initialization failed"
    exit 1
fi

echo "Database initialized successfully"

# Start the application
echo "Starting Flask application..."
python main.py 