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
import time

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
        logger.info("Loaded environment from .env.local")
    else:
        load_dotenv()
        logger.info("Loaded environment from .env")

    # Get database connection parameters
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "5432")
    admin_user = os.getenv("DB_ADMIN_USER", "postgres")
    admin_password = os.getenv("DB_ADMIN_PASSWORD", "postgres")

    app_user = os.getenv("DB_USER", "thunderbuddy")
    app_password = os.getenv("DB_PASSWORD", "localdev")
    app_db = os.getenv("DB_NAME", "thunderbuddy")

    logger.info(f"Connecting to database at {db_host}:{db_port} as {admin_user}")
    
    # Try multiple times to connect to the database
    max_retries = 5
    retry_delay = 3  # seconds
    
    for attempt in range(max_retries):
        try:
            # Connect to PostgreSQL as admin
            conn = psycopg2.connect(
                host=db_host,
                port=db_port,
                user=admin_user,
                password=admin_password,
                # Connect to default 'postgres' database initially
                database="postgres",
                connect_timeout=10
            )
            conn.autocommit = True
            cursor = conn.cursor()
            logger.info("Successfully connected to database")
            
            # Check if user exists
            cursor.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (app_user,))
            user_exists = cursor.fetchone() is not None

            if not user_exists:
                logger.info("Creating database user '%s'", app_user)
                cursor.execute(
                    "CREATE USER %s WITH PASSWORD %s",
                    (app_user, app_password)
                )
            else:
                logger.info("User '%s' already exists", app_user)

            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (app_db,))
            db_exists = cursor.fetchone() is not None

            if not db_exists:
                logger.info("Creating database '%s'", app_db)
                # Note: We can't use parameters for identifiers (table/database names)
                # but we've already validated these values by using them in parameterized
                # queries above
                quoted_db = psycopg2.extensions.quote_ident(app_db, conn)
                quoted_user = psycopg2.extensions.quote_ident(app_user, conn)
                cursor.execute(f"CREATE DATABASE {quoted_db} OWNER {quoted_user}")
            else:
                logger.info("Database '%s' already exists", app_db)
                # Ensure ownership
                quoted_db = psycopg2.extensions.quote_ident(app_db, conn)
                quoted_user = psycopg2.extensions.quote_ident(app_user, conn)
                cursor.execute(f"ALTER DATABASE {quoted_db} OWNER TO {quoted_user}")

            # Grant privileges
            quoted_db = psycopg2.extensions.quote_ident(app_db, conn)
            quoted_user = psycopg2.extensions.quote_ident(app_user, conn)
            cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {quoted_db} TO {quoted_user}")

            logger.info("Database initialization completed successfully")
            return True
            
        except Exception as error:
            logger.error("Database initialization attempt %d/%d failed: %s", 
                        attempt + 1, max_retries, str(error))
            if attempt < max_retries - 1:
                logger.info("Retrying in %d seconds...", retry_delay)
                time.sleep(retry_delay)
            else:
                logger.error("All database initialization attempts failed")
                return False
        finally:
            if 'conn' in locals() and conn is not None:
                conn.close()


if __name__ == "__main__":
    SUCCESS = init_db_user()
    sys.exit(0 if SUCCESS else 1)
