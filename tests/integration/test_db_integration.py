"""Integration tests for database functionality"""

import os

import psycopg2
import pytest


@pytest.fixture(scope="session")
def database_url():
    """Fixture to provide database URL for integration tests"""
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.skip("DATABASE_URL not set")
    return url


@pytest.mark.integration
def test_db_connection_integration(database_url):
    """Test actual database connection if environment is set up"""
    try:
        conn = psycopg2.connect(database_url)
        cur = conn.cursor()
        cur.execute("SELECT 1")
        result = cur.fetchone()
        cur.close()
        conn.close()
        assert result[0] == 1
    except psycopg2.Error as e:
        pytest.skip(f"Database is not accessible: {e}")
