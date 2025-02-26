"""
Global pytest configuration and fixtures.

This file contains setup code and fixtures that will be available to all tests.
It configures the test environment and provides mock objects for testing.
"""

import os
import sys
from unittest.mock import patch

import pytest

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def pytest_configure(config):
    """
    Configure the test environment.

    This function is called before tests are collected.
    It sets up environment variables for testing.
    """
    # Set test database URL to match the one used in Makefile
    if 'DATABASE_URL' not in os.environ:
        os.environ['DATABASE_URL'] = (
            'postgresql://thunderbuddy:localdev@localhost:5432/thunderbuddy'
        )

    # Ensure we have a test API key
    if 'WEATHERBIT_API_KEY' not in os.environ:
        os.environ['WEATHERBIT_API_KEY'] = 'test_api_key'


@pytest.fixture
def mock_db_connection():
    """
    Mock the database connection for tests.

    This fixture patches the database connection function to prevent
    actual database connections during testing.
    """
    with patch('scripts.db.test_connection') as mock_conn:
        # Configure the mock connection
        mock_conn.return_value = {
            'connection': 'healthy',
            'query': 'healthy',
            'message': 'Mock DB connection successful'
        }
        yield mock_conn
