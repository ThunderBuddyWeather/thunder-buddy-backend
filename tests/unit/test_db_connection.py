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


@pytest.fixture(scope="session", autouse=True)
def mock_db_connection():
    with patch("scripts.db.get_engine") as mock_engine:
        # Configure the mock to return a working engine
        mock_conn = mock_engine.return_value.connect.return_value.__enter__.return_value
        mock_conn.execute.return_value.scalar.return_value = 1
        yield mock_engine


@pytest.mark.unit
def test_connection_basic(mock_db_connection):
    """Test basic connection function returns a dictionary"""
    result = db_test_connection()
    assert isinstance(result, dict)


@pytest.mark.unit
def test_connection_response_structure(mock_db_connection):
    """Test connection response has expected keys"""
    result = db_test_connection()
    assert "connection" in result
    assert "query" in result
    assert "message" in result


@pytest.mark.unit
def test_db_connection_success(mock_db_connection):
    """Test successful database connection"""
    result = db_test_connection()
    assert result["connection"] == "healthy"
    assert result["query"] == "healthy"
    assert "successful" in result["message"].lower()


@pytest.mark.unit
def test_db_connection_failure(mock_db_connection):
    """Test database connection failure handling"""
    # Mock the get_engine function to raise an exception
    mock_db_connection.side_effect = SQLAlchemyError("Test error")
    
    result = db_test_connection()
    assert result["connection"] == "unhealthy"
    assert result["query"] == "unhealthy"
    assert "failed" in result["message"].lower()
    
    # Reset the mock for other tests
    mock_db_connection.side_effect = None


@pytest.mark.unit
def test_db_connection_missing_url(mock_db_connection):
    """Test handling of missing database URL"""
    # Mock the get_engine function to raise a ValueError
    mock_db_connection.side_effect = ValueError("DATABASE_URL not set")
    
    result = db_test_connection()
    assert result["connection"] == "unhealthy"
    assert result["query"] == "unhealthy"
    assert "configuration error" in result["message"].lower()
    
    # Reset the mock for other tests
    mock_db_connection.side_effect = None
