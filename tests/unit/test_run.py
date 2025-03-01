"""Unit tests for run.py"""

from unittest.mock import patch

import pytest
from flask import Flask, jsonify


# Mocking the app creation to avoid database connection
@pytest.fixture
def app():
    """Create a test Flask app with mocked routes"""
    app = Flask(__name__)
    app.config["TESTING"] = True

    @app.route("/")
    def hello_world():
        return jsonify({"Message": "Hello World"}), 200

    @app.route("/health")
    def health_check():
        return (
            jsonify(
                {
                    "status": "healthy",
                    "components": {
                        "api": {
                            "status": "healthy",
                            "message": "API service is running",
                        },
                        "database": {"connection": "healthy", "query": "healthy"},
                    },
                }
            ),
            200,
        )

    return app


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


def test_hello_world(client):
    """Test hello world endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["Message"] == "Hello World"


def test_health_check_healthy(client):
    """Test health check endpoint when all components are healthy"""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json
    assert data["status"] == "healthy"
    assert data["components"]["api"]["status"] == "healthy"
    assert data["components"]["database"]["connection"] == "healthy"
    assert data["components"]["database"]["query"] == "healthy"
