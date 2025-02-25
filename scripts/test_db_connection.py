#!/usr/bin/env python3
"""Test database connectivity using SQLAlchemy"""

import os
import sys
from pathlib import Path
from typing import Dict

# Add the project root to the Python path to allow importing from scripts
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Import dotenv for environment variable loading
from dotenv import load_dotenv

# Find and load environment variables from project root
env_path = project_root / ".env.local"
load_dotenv(env_path)

# Print for debugging
print(f"Loading env from: {env_path}")

# Modify DATABASE_URL to use localhost instead of 'db' when running locally
database_url = os.getenv("DATABASE_URL", "")
if "db:" in database_url:
    local_db_url = database_url.replace("db:", "localhost:")
    print(f"Original DATABASE_URL: {database_url}")
    print(f"Modified for local testing: {local_db_url}")
    os.environ["DATABASE_URL"] = local_db_url

# Now import the database module after setting the correct DATABASE_URL
from scripts.db import test_connection as sqlalchemy_test_connection  # noqa: E402

print(f"Using DATABASE_URL: {os.getenv('DATABASE_URL')}")


def test_connection(database_url=None) -> Dict[str, str]:
    """Test database connection using environment variables or provided URL"""
    # If a database_url is provided, temporarily set it in the environment
    original_url = None
    if database_url:
        original_url = os.environ.get("DATABASE_URL")
        os.environ["DATABASE_URL"] = database_url

    try:
        # Use our new SQLAlchemy-based test_connection function
        return sqlalchemy_test_connection()
    finally:
        # Restore the original DATABASE_URL if we changed it
        if database_url and original_url is not None:
            os.environ["DATABASE_URL"] = original_url
        elif database_url and original_url is None:
            del os.environ["DATABASE_URL"]


if __name__ == "__main__":
    result = test_connection()
    print("Database Health Check Results:")
    print(f"Connection: {result['connection']}")
    print(f"Query: {result['query']}")
    print(f"Message: {result['message']}")
    sys.exit(
        0 if result["connection"] == "healthy" and result["query"] == "healthy" else 1
    )
