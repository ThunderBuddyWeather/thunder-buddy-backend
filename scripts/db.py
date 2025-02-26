"""Database utilities and connection management"""

import os
from typing import Dict

# pylint: disable=import-error
from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError

# Global engine instance
_engine = None


def get_engine() -> Engine:
    """
    Get or create SQLAlchemy engine
    Returns a singleton engine instance
    """
    global _engine

    if _engine is None:
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")
        _engine = create_engine(database_url)

    return _engine


def test_connection() -> Dict[str, str]:
    """
    Test database connection using SQLAlchemy
    Returns a dictionary with connection status information
    """
    db_status = {
        "connection": "unhealthy",
        "query": "unhealthy",
        "message": "Not checked",
    }

    try:
        # Get or create engine
        engine = get_engine()

        # Test basic connection by creating a connection
        with engine.connect() as connection:
            db_status["connection"] = "healthy"

            # Test query execution
            query_result = connection.execute(text("SELECT 1")).scalar()
            if query_result == 1:
                db_status["query"] = "healthy"
                db_status["message"] = "Database connection and query successful"
            else:
                db_status["message"] = "Query returned unexpected result"

    except ValueError as error:
        db_status["message"] = f"Database configuration error: {str(error)}"
    except SQLAlchemyError as error:
        db_status["message"] = f"Database check failed: {str(error)}"

    return db_status
