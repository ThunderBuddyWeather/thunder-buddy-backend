"""
Global pytest configuration and fixtures.

This file contains setup code and fixtures that will be available to all tests.
It configures the test environment and provides mock objects for testing.
"""

import os
import sys
from unittest.mock import MagicMock, patch

import pytest
from flask import Flask

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Check if running in CI environment
IN_CI = os.environ.get("CI") == "true"


def pytest_configure(config):  # pylint: disable=unused-argument
    """
    Configure the test environment.

    This function is called before tests are collected.
    It sets up environment variables for testing.
    """
    # Set test database URL to match the one used in Makefile
    if "TEST_DATABASE_URL" in os.environ:
        # If TEST_DATABASE_URL is set (like in CI), use it
        os.environ["DATABASE_URL"] = os.environ["TEST_DATABASE_URL"]
    elif "DATABASE_URL" not in os.environ:
        # Otherwise use a default local test database
        os.environ["DATABASE_URL"] = (
            "postgresql://thunderbuddy:localdev@localhost:5432/thunderbuddy"
        )

    # Ensure we have a test API key
    if "WEATHERBIT_API_KEY" not in os.environ:
        os.environ["WEATHERBIT_API_KEY"] = "test_api_key"


# Optional mock fixtures for tests that don't need a real database
@pytest.fixture
def mock_app():
    """
    Create a test Flask app with no database dependency
    """
    app = Flask(__name__)
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"

    return app


@pytest.fixture
def mock_client(mock_app):
    """
    Create a test client for the mock app
    """
    return mock_app.test_client()
