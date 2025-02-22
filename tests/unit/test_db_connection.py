"""Unit tests for database connection functionality"""
import os
from unittest.mock import patch
import pytest
import psycopg2
from scripts.test_db_connection import test_connection

@pytest.fixture
def database_url():
    """Fixture to manage DATABASE_URL environment variable"""
    test_url = 'postgresql://user:pass@localhost:5432/db'
    original_url = os.environ.get('DATABASE_URL')
    os.environ['DATABASE_URL'] = test_url
    yield test_url
    if original_url:
        os.environ['DATABASE_URL'] = original_url
    else:
        del os.environ['DATABASE_URL']

def test_basic_connection(database_url):
    """Test basic connection function"""
    with patch('psycopg2.connect', side_effect=psycopg2.Error('Connection failed')):
        result = test_connection(database_url)
        assert result is False

def test_db_connection_success(database_url):
    """Test successful database connection"""
    with patch('psycopg2.connect') as mock_connect:
        # Mock the cursor and its execute method
        mock_cursor = mock_connect.return_value.cursor.return_value
        
        # Run the test
        result = test_connection(database_url)
        assert result is True
        
        # Verify the connection was attempted with correct URL
        mock_connect.assert_called_once_with(database_url)
        mock_cursor.execute.assert_called_once_with('SELECT 1')

def test_db_connection_failure(database_url):
    """Test database connection failure"""
    with patch('psycopg2.connect', side_effect=psycopg2.Error('Connection failed')):
        result = test_connection(database_url)
        assert result is False

def test_db_connection_missing_url():
    """Test database connection with missing URL"""
    if 'DATABASE_URL' in os.environ:
        del os.environ['DATABASE_URL']
    result = test_connection(None)
    assert result is False
