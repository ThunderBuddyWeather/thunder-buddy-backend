#!/usr/bin/env python3
"""
Database initialization script for Thunder Buddy

This script creates the necessary database user and database
if they don't already exist. It's designed to be run during
container initialization to ensure the database is properly set up.
"""

import logging
import os
import sys

import psycopg2
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("db_init")

def init_db_user():
    """
    Initialize the database user and database.
    
    This connects to PostgreSQL with admin credentials and creates:
    1. The application user if it doesn't exist
    2. The application database if it doesn't exist
    3. Grants necessary permissions
    """
    # Load environment variables
    if os.path.exists(".env.local"):
        load_dotenv(dotenv_path=".env.local")
    else:
        load_dotenv()
    
    # Get database connection parameters
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    admin_user = os.getenv("DB_ADMIN_USER", "postgres")
    admin_password = os.getenv("DB_ADMIN_PASSWORD", "postgres")
    
    app_user = os.getenv("DB_USER", "thunderbuddy")
    app_password = os.getenv("DB_PASSWORD", "localdev")
    app_db = os.getenv("DB_NAME", "thunderbuddy")
    
    # Connect to PostgreSQL as admin
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            user=admin_user,
            password=admin_password,
            # Connect to default 'postgres' database initially
            database="postgres"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Check if user exists
        cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (app_user,))
        user_exists = cursor.fetchone() is not None
        
        if not user_exists:
            logger.info(f"Creating database user '{app_user}'")
            cursor.execute("CREATE USER %s WITH PASSWORD %s", (app_user, app_password))
        else:
            logger.info(f"User '{app_user}' already exists")
        
        # Check if database exists
        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (app_db,))
        db_exists = cursor.fetchone() is not None
        
        if not db_exists:
            logger.info(f"Creating database '{app_db}'")
            cursor.execute(f"CREATE DATABASE {app_db} OWNER {app_user}")
        else:
            logger.info(f"Database '{app_db}' already exists")
            # Ensure ownership
            cursor.execute(f"ALTER DATABASE {app_db} OWNER TO {app_user}")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {app_db} TO {app_user}")
        
        logger.info("Database initialization completed successfully")
        return True
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        return False
    finally:
        if 'conn' in locals() and conn is not None:
            conn.close()

if __name__ == "__main__":
    success = init_db_user()
    sys.exit(0 if success else 1) 