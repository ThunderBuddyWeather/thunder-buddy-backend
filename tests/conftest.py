"""
Global pytest configuration and fixtures.
This file is automatically loaded by pytest before any tests are run.
"""

import os
import sys
from unittest.mock import patch

import pytest


# Set up test environment variables before any modules are imported
def pytest_configure(config):
    """Configure the test environment before tests are run."""
    # Set a test database URL to prevent connection errors during test collection
    # Only set if not already set (to allow integration tests to use real DB)
    if "DATABASE_URL" not in os.environ:
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
    
    # Add any other environment variables needed for testing
    if "WEATHERBIT_API_KEY" not in os.environ:
        os.environ["WEATHERBIT_API_KEY"] = "test_api_key"


@pytest.fixture(scope="session", autouse=True)
def mock_db_connection(request):
    """
    Mock database connection for unit tests.
    This prevents actual database connections during testing.
    
    For integration tests marked with the 'integration' marker,
    this fixture will not apply, allowing real database connections.
    """
    # Skip mocking for integration tests
    markers = [marker.name for marker in request.node.iter_markers()]
    if "integration" in markers:
        # Don't mock for integration tests
        yield None
        return
        
    # Mock for unit tests
    with patch("scripts.db.get_engine") as mock_engine:
        # Configure the mock to return a working engine
        mock_conn = mock_engine.return_value.connect.return_value.__enter__.return_value
        mock_conn.execute.return_value.scalar.return_value = 1
        yield mock_engine 