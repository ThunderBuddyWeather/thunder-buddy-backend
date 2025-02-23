"""Unit tests for database connection functionality"""

import os
from unittest.mock import patch

import psycopg2
import pytest

from scripts.test_db_connection import test_connection


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
def test_connection_response_structure():
    """Test basic connection response structure"""
    result = test_connection(None)
    assert isinstance(result, dict)
    assert all(k in result for k in ["connection", "query", "message"])
    assert result["connection"] in ["healthy", "unhealthy"]
    assert result["query"] in ["healthy", "unhealthy"]
    assert isinstance(result["message"], str)


@pytest.mark.unit
def test_db_connection_success(database_url):
    """Test successful database connection"""
    with patch("psycopg2.connect") as mock_connect, \
         patch("scripts.test_db_connection.create_engine") as mock_engine:
        # Setup mock engine
        mock_conn = mock_engine.return_value.connect.return_value.__enter__.return_value
        mock_conn.execute.return_value.scalar.return_value = 1

        # Setup psycopg2 mock
        mock_connect.return_value.close = lambda: None

        # Run the test
        result = test_connection(database_url)
        assert result["connection"] == "healthy"
        assert result["query"] == "healthy"
        assert "successful" in result["message"]


@pytest.mark.unit
def test_db_connection_failure(database_url):
    """Test database connection failure"""
    with patch("psycopg2.connect", side_effect=psycopg2.Error("Connection failed")):
        result = test_connection(database_url)
        assert result["connection"] == "unhealthy"
        assert result["query"] == "unhealthy"
        assert "Connection failed" in result["message"]


@pytest.mark.unit
def test_db_connection_missing_url():
    """Test database connection with missing URL"""
    if "DATABASE_URL" in os.environ:
        del os.environ["DATABASE_URL"]
    result = test_connection(None)
    assert result["connection"] == "unhealthy"
    assert result["query"] == "unhealthy"
    assert "DATABASE_URL" in result["message"]
