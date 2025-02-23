#!/usr/bin/env python3
"""Test database connectivity using psycopg2"""

import os
import sys
from pathlib import Path
from typing import Dict

# pylint: disable=import-error
import psycopg2  # type: ignore
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Find and load environment variables from project root
project_root = Path(__file__).parent.parent
env_path = project_root / '.env.local'
load_dotenv(env_path)

# Print for debugging
print(f"Loading env from: {env_path}")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")

def test_connection(database_url=None) -> Dict[str, str]:
    """Test database connection using environment variables or provided URL"""
    db_status = {
        "connection": "unhealthy",
        "query": "unhealthy",
        "message": "Not checked"
    }

    try:
        # Use provided URL or fall back to environment variable
        conn_url = database_url or os.environ["DATABASE_URL"]
        
        # Test basic connection
        conn = psycopg2.connect(conn_url)
        conn.close()
        db_status["connection"] = "healthy"
        
        # Test query execution
        engine = create_engine(conn_url)
        with engine.connect() as connection:
            result = connection.execute(text('SELECT 1')).scalar()
            if result == 1:
                db_status["query"] = "healthy"
                db_status["message"] = "Database connection and query successful"
            else:
                db_status["message"] = "Query returned unexpected result"

    except (psycopg2.Error, KeyError) as e:
        db_status["message"] = f"Database check failed: {str(e)}"

    return db_status


if __name__ == "__main__":
    result = test_connection()
    print("Database Health Check Results:")
    print(f"Connection: {result['connection']}")
    print(f"Query: {result['query']}")
    print(f"Message: {result['message']}")
    sys.exit(0 if result["connection"] == "healthy" and result["query"] == "healthy" else 1)
