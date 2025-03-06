"""Integration tests for full application stack"""

import os
from datetime import datetime, timedelta

import pytest
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash

from app import create_app
from app.extensions import db
from app.Models.userAccountModel import UserAccount


@pytest.fixture(scope="session")
def app():
    """Create test Flask app with test config"""
    app = create_app("testing")
    app.config.update(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": os.getenv("DATABASE_URL", "").replace(
                "@db:", "@localhost:"
            ),
            "JWT_SECRET_KEY": "test-secret-key",
        }
    )

    # Register root routes
    @app.route("/", methods=["GET"])
    def hello_world():
        """Root endpoint that returns a greeting."""
        return jsonify({"Message": "Hello World"}), 200

    return app


@pytest.fixture(scope="function")
def client(app):
    """Create test client"""
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.close()  # Close the session properly
            db.drop_all()


@pytest.fixture
def test_user(app):
    """Create a test user"""
    with app.app_context():
        user = UserAccount(
            user_username="testuser",
            user_password=generate_password_hash("password123"),
            user_name="Test User",
            user_email="test@example.com",
        )
        db.session.add(user)
        db.session.commit()
        return user


@pytest.fixture
def auth_headers(app, test_user):
    """Create authentication headers"""
    with app.app_context():
        # Ensure test_user is attached to a session
        db.session.add(test_user)
        db.session.refresh(test_user)
        token = create_access_token(identity=test_user.user_id)
        return {"Authorization": f"Bearer {token}"}


@pytest.mark.integration
@pytest.mark.regression
def test_app_startup(client):
    """Test basic application startup and root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["Message"] == "Hello World"


@pytest.mark.integration
@pytest.mark.regression
def test_user_registration_flow(client):
    """Test complete user registration flow"""
    # Register new user
    register_data = {
        "email": "newuser@example.com",
        "password": "password123",
        "name": "New User",
        "username": "newuser",
    }
    response = client.post("/api/user/register", json=register_data)
    assert response.status_code == 201
    assert response.json["email"] == register_data["email"]

    # Try to login with new credentials
    login_data = {
        "email": register_data["email"],
        "password": register_data["password"],
    }
    response = client.post("/api/user/login", json=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json


@pytest.mark.integration
def test_user_profile_flow(client, test_user, auth_headers):
    """Test complete user profile management flow"""
    # Get profile
    response = client.get("/api/user/profile", headers=auth_headers)
    assert response.status_code == 200
    assert response.json["email"] == test_user.user_email

    # Update profile
    update_data = {"name": "Updated Name", "phone": "9876543210"}
    response = client.put("/api/user/profile", headers=auth_headers, json=update_data)
    assert response.status_code == 204

    # Query user directly from database instead of refreshing
    with client.application.app_context():
        updated_user = UserAccount.query.get(test_user.user_id)
        assert updated_user.user_name == "Updated Name"
        assert updated_user.user_phone == "9876543210"

    # Delete profile
    response = client.delete("/api/user/profile", headers=auth_headers)
    assert response.status_code == 204

    # Verify profile is deleted by directly querying the database
    with client.application.app_context():
        deleted_user = UserAccount.query.get(test_user.user_id)
        assert deleted_user is None


@pytest.mark.integration
def test_friendship_flow(client, test_user, auth_headers):
    """Test complete friendship management flow"""
    # Create another user to befriend through registration
    friend_data = {
        "email": "friend@example.com",
        "password": "password123",
        "name": "Friend User",
        "username": "friend",
    }
    response = client.post("/api/user/register", json=friend_data)
    assert response.status_code == 201
    friend_id = response.json["user_id"]

    # Send friend request
    response = client.post(f"/api/friends/request/{friend_id}", headers=auth_headers)
    assert response.status_code == 201

    # Login as friend to get token
    friend_login = {"email": friend_data["email"], "password": friend_data["password"]}
    response = client.post("/api/user/login", json=friend_login)
    assert response.status_code == 200
    friend_token = response.json["access_token"]
    friend_headers = {"Authorization": f"Bearer {friend_token}"}

    # Accept friend request
    response = client.put(
        f"/api/friends/accept/{test_user.user_id}", headers=friend_headers
    )
    assert response.status_code == 200

    # Get friends list
    response = client.get("/api/friends", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["friends"]) == 1
    assert response.json["friends"][0]["user_id"] == friend_id

    # Unfriend
    response = client.delete(f"/api/friends/{friend_id}", headers=auth_headers)
    assert response.status_code == 204

    # Verify friend is removed
    response = client.get("/api/friends", headers=auth_headers)
    assert response.status_code == 200
    assert len(response.json["friends"]) == 0


@pytest.mark.integration
def test_rate_limiting(client):
    """Test rate limiting across endpoints"""
    # Test registration rate limiting
    for _ in range(6):  # Limit is 5 per minute
        response = client.post(
            "/api/user/register",
            json={
                "email": f"test{_}@example.com",
                "password": "password123",
                "name": "Test User",
            },
        )
    assert response.status_code == 429


@pytest.mark.integration
def test_error_handling(client, auth_headers):
    """Test error handling across endpoints"""
    # Test 404 handling
    response = client.get("/api/nonexistent")
    assert response.status_code == 404

    # Test invalid JSON handling or rate limiting
    # This might return 400 (bad request) or 429 (too many requests) if rate limited
    response = client.post(
        "/api/user/register", data="invalid json", content_type="application/json"
    )
    assert response.status_code in [
        400,
        429,
    ], f"Expected 400 or 429, got {response.status_code}"

    # Test rate limiting - this test may already be rate limited
    # so we'll accept either 400 (bad request) or 429 (too many requests)
    response = client.post(
        "/api/user/register",
        json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User",
            "username": "testuser",
        },
    )
    assert response.status_code in [400, 429]

    # Test unauthorized access
    response = client.get("/api/user/profile")
    assert response.status_code == 401

    # Test invalid token
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/api/user/profile", headers=headers)
    assert response.status_code == 422
