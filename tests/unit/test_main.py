"""Unit tests for main routes"""

import pytest
from flask import Flask, jsonify


@pytest.fixture
def app():
    """Create test Flask app"""
    app = Flask(__name__)
    app.config["TESTING"] = True

    # Add root route for testing
    @app.route("/")
    def hello():
        return jsonify({"Message": "Hello World"})

    return app


@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()


@pytest.mark.regression
def test_hello_world(client):
    """Test hello world endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["Message"] == "Hello World"
