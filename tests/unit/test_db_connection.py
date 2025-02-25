"""Unit tests for database connection functionality"""

import os
from unittest.mock import patch

import psycopg2
import pytest
from sqlalchemy import create_engine
from sqlalchemy.exc import SQLAlchemyError

from scripts.db import test_connection as db_test_connection


@pytest.fixture
def database_url():
    """Fixture to manage DATABASE_URL environment variable"""
    test_url = "postgresql://user:pass@localhost:5432/db"
    original_url = os.environ.get("DATABASE_URL")
    os.environ["DATABASE_URL"] = test_url
    yield test_url
    if original_url:
        os.environ["DATABASE_URL"] = original_url
    else:
        del os.environ["DATABASE_URL"]


@pytest.mark.unit
def test_connection_basic():
    """Test basic connection function returns expected structure"""
    result = db_test_connection()
    assert isinstance(result, dict)
    assert all(k in result for k in ["connection", "query", "message"])


@pytest.mark.unit
def test_connection_response_structure():
    """Test basic connection response structure"""
    result = db_test_connection()
    assert isinstance(result, dict)
    assert all(k in result for k in ["connection", "query", "message"])
    assert result["connection"] in ["healthy", "unhealthy"]
    assert result["query"] in ["healthy", "unhealthy"]
    assert isinstance(result["message"], str)


@pytest.mark.unit
def test_db_connection_success(database_url):
    """Test successful database connection"""
    with patch("scripts.db.get_engine") as mock_get_engine:
        # Setup mock engine
        mock_engine = mock_get_engine.return_value
        mock_conn = mock_engine.connect.return_value.__enter__.return_value
        mock_conn.execute.return_value.scalar.return_value = 1

        # Run the test
        result = db_test_connection()
        
        # Verify results
        assert result["connection"] == "healthy"
        assert result["query"] == "healthy"
        assert "successful" in result["message"]


@pytest.mark.unit
def test_db_connection_failure(database_url):
    """Test database connection failure"""
    with patch("scripts.db.get_engine", side_effect=SQLAlchemyError("Connection failed")):
        # Run the test - the exception should be caught inside db_test_connection
        result = db_test_connection()
        
        # Verify results
        assert result["connection"] == "unhealthy"
        assert result["query"] == "unhealthy"
        assert "failed" in result["message"]


@pytest.mark.unit
def test_db_connection_missing_url():
    """Test database connection with missing URL"""
    # Save original DATABASE_URL if it exists
    original_url = os.environ.get("DATABASE_URL")
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    
    try:
        with patch("scripts.db.get_database_url", return_value=""):
            with patch("scripts.db.get_engine", side_effect=ValueError("DATABASE_URL environment variable is not set")):
                # Run the test
                result = db_test_connection()
                
                # Verify results
                assert result["connection"] == "unhealthy"
                assert result["query"] == "unhealthy"
                assert "configuration error" in result["message"]
    finally:
        # Restore original DATABASE_URL if it existed
        if original_url:
            os.environ["DATABASE_URL"] = original_url


@pytest.fixture(scope="session", autouse=True)
def mock_db_connection():
    with patch("scripts.db.get_engine") as mock_engine:
        # Configure the mock to return a working engine
        mock_conn = mock_engine.return_value.connect.return_value.__enter__.return_value
        mock_conn.execute.return_value.scalar.return_value = 1
        yield mock_engine
