"""
Unit tests for database connection functionality.

These tests verify that the database connection functions work correctly
and handle various error conditions appropriately.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
from psycopg2 import OperationalError
from sqlalchemy.exc import SQLAlchemyError

from scripts.db import test_connection as get_db_connection


@pytest.mark.regression
def test_connection_basic():
    """Test that the connection function returns a dictionary."""
    with patch("scripts.db.get_engine") as mock_engine:
        # Configure the mock
        mock_engine.return_value = MagicMock()
        # Call the function
        result = get_db_connection()
        # Verify the result
        assert isinstance(result, dict)
        assert "connection" in result
        assert "message" in result


def test_connection_response_structure():
    """Test that the connection response has the expected structure."""
    with patch("scripts.db.get_engine") as mock_engine:
        # Configure the mock
        mock_engine.return_value = MagicMock()
        # Call the function
        result = get_db_connection()
        # Verify the structure
        assert result["connection"] == "healthy"
        assert isinstance(result["message"], str)
        assert "query" in result


@pytest.mark.regression
def test_db_connection_success():
    """Test successful database connection."""
    with patch("scripts.db.get_engine") as mock_engine:
        # Configure the mock connection
        mock_conn = MagicMock()
        mock_conn.execute().scalar.return_value = 1
        mock_engine.return_value.connect.return_value.__enter__.return_value = mock_conn

        # Call the function
        result = get_db_connection()

        # Verify the result
        assert result["connection"] == "healthy"
        assert result["query"] == "healthy"
        assert "successful" in result["message"]


def test_db_connection_failure():
    """Test database connection failure."""
    with patch("scripts.db.get_engine") as mock_engine:
        # Set up the mock engine
        mock_engine_instance = MagicMock()
        mock_engine.return_value = mock_engine_instance

        # Make the connect method raise a SQLAlchemy exception when called
        mock_engine_instance.connect.side_effect = SQLAlchemyError("Connection refused")

        # Call the function
        result = get_db_connection()

        # Verify the result
        assert result["connection"] == "unhealthy"
        assert "Database check failed" in result["message"]


def test_db_connection_missing_url():
    """Test behavior when DATABASE_URL environment variable is missing."""
    # Save the current environment variable
    original_url = os.environ.get("DATABASE_URL")
    try:
        # Remove the environment variable
        if "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]

        # Patch get_engine to raise a ValueError when called
        with patch("scripts.db.get_engine") as mock_engine:
            error_msg = "DATABASE_URL environment variable is not set"
            mock_engine.side_effect = ValueError(error_msg)

            # Call the function
            result = get_db_connection()

            # Verify the result
            assert result["connection"] == "unhealthy"
            assert "Database configuration error" in result["message"]
    finally:
        # Restore the environment variable
        if original_url is not None:
            os.environ["DATABASE_URL"] = original_url
