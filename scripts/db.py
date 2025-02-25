#!/usr/bin/env python3
"""
Database module for Thunder Buddy application
Provides standardized SQLAlchemy-based database access
"""

import logging
import os
from typing import Any, Dict, Optional

from sqlalchemy import Engine, create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.pool import QueuePool

# Configure logging
logger = logging.getLogger(__name__)

# Global engine instance
_engine: Optional[Engine] = None


def get_database_url() -> str:
    """Get database URL from environment variables"""
    return os.environ.get("DATABASE_URL", "")


def get_engine() -> Engine:
    """
    Get or create SQLAlchemy engine with connection pooling
    Returns a singleton engine instance
    """
    global _engine

    if _engine is None:
        database_url = get_database_url()
        if not database_url:
            raise ValueError("DATABASE_URL environment variable is not set")

        # Create engine with connection pooling
        _engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=5,                # Default connection pool size
            max_overflow=10,            # Allow up to 10 connections to overflow
            pool_timeout=30,            # Wait up to 30 seconds for a connection
            pool_recycle=1800,          # Recycle connections after 30 minutes
            pool_pre_ping=True,         # Verify connections before using them
        )

        logger.info("Database engine initialized with connection pooling")

    return _engine


# Create a scoped session factory
# This ensures thread safety when used in a multi-threaded environment
SessionFactory = scoped_session(sessionmaker())


def init_db() -> None:
    """Initialize database connection"""
    engine = get_engine()
    SessionFactory.configure(bind=engine)
    logger.info("Database session factory configured")


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


def execute_query(query: str, params: Optional[Dict[str, Any]] = None) -> Any:
    """
    Execute a SQL query using SQLAlchemy

    Args:
        query: SQL query string
        params: Optional parameters for the query

    Returns:
        Query result

    Raises:
        SQLAlchemyError: If the query fails
    """
    if params is None:
        params = {}

    try:
        # Create a new session
        session = SessionFactory()

        try:
            # Execute query
            result = session.execute(text(query), params)
            return result
        finally:
            # Always close the session
            session.close()
    except SQLAlchemyError as error:
        logger.error("Database query failed: %s", str(error))
        raise
