"""Unit tests for user account controller"""

from unittest.mock import Mock, patch

import pytest
from flask import Flask, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import check_password_hash

from app.Controllers.userAccountController import (
    delete_user_account,
    get_user_account,
    save_user_account,
    update_user_account,
)
from app.extensions import db
from app.Models.userAccountModel import UserAccount


@pytest.fixture
def app():
    """Create a test Flask app"""
    app = Flask(__name__)
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    with app.app_context():
        db.init_app(app)
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()


def test_save_user_account_success(app):
    """Test successful user account creation"""
    test_data = {
        "user_username": "testuser",
        "user_password": "password123",
        "user_name": "Test User",
        "user_email": "test@example.com",
        "user_phone": "1234567890",
        "user_address": "123 Test St",
        "user_location": "Test City",
        "user_weather": "sunny",
        "user_profile_picture": "profile.jpg",
    }

    with app.test_request_context(json=test_data):
        response, status_code = save_user_account()
        assert status_code == 201
        assert response.json["message"] == "User account saved"


def test_save_user_account_missing_fields(app):
    """Test user account creation with missing fields"""
    test_data = {
        "user_username": "testuser",
        "user_password": "password123",
        # Missing other required fields
    }

    with app.test_request_context(json=test_data):
        response, status_code = save_user_account()
        assert status_code == 400
        assert "Invalid input" in response.json["message"]


def test_save_user_account_no_data(app):
    """Test user account creation with no data"""
    with app.test_request_context(
        json={}, content_type="application/json"  # Empty JSON object instead of None
    ):
        response, status_code = save_user_account()
        assert status_code == 400
        assert response.json["message"] == "Invalid input"


@patch("app.Controllers.userAccountController.db.session.commit")
def test_save_user_account_db_error(mock_commit, app):
    """Test user account creation with database error"""
    mock_commit.side_effect = SQLAlchemyError("Database error")

    test_data = {
        "user_username": "testuser",
        "user_password": "password123",
        "user_name": "Test User",
        "user_email": "test@example.com",
        "user_phone": "1234567890",
        "user_address": "123 Test St",
        "user_location": "Test City",
        "user_weather": "sunny",
        "user_profile_picture": "profile.jpg",
    }

    with app.test_request_context(json=test_data):
        response, status_code = save_user_account()
        assert status_code == 500
        assert "Database error" in response.json["message"]


def test_get_user_account_success(app):
    """Test successful user account retrieval"""
    with app.app_context():
        # Create a test user
        user = UserAccount(
            user_username="testuser",
            user_password="password123",
            user_name="Test User",
            user_email="test@example.com",
            user_phone="1234567890",
            user_address="123 Test St",
            user_location="Test City",
            user_weather="sunny",
            user_profile_picture="profile.jpg",
        )
        db.session.add(user)
        db.session.commit()

        response, status_code = get_user_account(user.user_id)
        assert status_code == 200
        assert response.json["user_username"] == "testuser"
        assert response.json["user_email"] == "test@example.com"


def test_get_user_account_not_found(app):
    """Test user account retrieval for non-existent user"""
    with app.app_context():
        response, status_code = get_user_account(999)
        assert status_code == 404
        assert "not found" in response.json["message"]


@patch("app.Controllers.userAccountController.UserAccount.query")
def test_get_user_account_db_error(mock_query, app):
    """Test user account retrieval with database error"""
    mock_query.filter_by.side_effect = SQLAlchemyError("Database error")

    with app.app_context():
        response, status_code = get_user_account(1)
        assert status_code == 500
        assert "Database error" in response.json["message"]


def test_update_user_account_success(app):
    """Test successful user account update"""
    with app.app_context():
        # Create a test user
        user = UserAccount(
            user_username="testuser",
            user_password="password123",
            user_name="Test User",
            user_email="test@example.com",
            user_phone="1234567890",
            user_address="123 Test St",
            user_location="Test City",
            user_weather="sunny",
            user_profile_picture="profile.jpg",
        )
        db.session.add(user)
        db.session.commit()

        test_data = {"user_name": "Updated Name", "user_email": "updated@example.com"}

        with app.test_request_context(json=test_data):
            response, status_code = update_user_account(user.user_id)
            assert status_code == 200
            assert response.json["message"] == "User account updated"

            # Verify changes in database
            updated_user = db.session.get(UserAccount, user.user_id)
            assert updated_user.user_name == "Updated Name"
            assert updated_user.user_email == "updated@example.com"


def test_update_user_account_all_fields(app):
    """Test updating all user account fields"""
    with app.app_context():
        # Create a test user
        user = UserAccount(
            user_username="testuser",
            user_password="password123",
            user_name="Test User",
            user_email="test@example.com",
            user_phone="1234567890",
            user_address="123 Test St",
            user_location="Test City",
            user_weather="sunny",
            user_profile_picture="profile.jpg",
        )
        db.session.add(user)
        db.session.commit()

        test_data = {
            "user_username": "newusername",
            "user_password": "newpassword",
            "user_name": "New Name",
            "user_email": "new@example.com",
            "user_phone": "9876543210",
            "user_address": "456 New St",
            "user_location": "New City",
            "user_weather": "rainy",
            "user_profile_picture": "new_profile.jpg",
        }

        with app.test_request_context(json=test_data):
            response, status_code = update_user_account(user.user_id)
            assert status_code == 200
            assert response.json["message"] == "User account updated"

            # Verify all changes in database
            updated_user = db.session.get(UserAccount, user.user_id)
            assert updated_user.user_username == "newusername"
            assert check_password_hash(updated_user.user_password, "newpassword")
            assert updated_user.user_name == "New Name"
            assert updated_user.user_email == "new@example.com"
            assert updated_user.user_phone == "9876543210"
            assert updated_user.user_address == "456 New St"
            assert updated_user.user_location == "New City"
            assert updated_user.user_weather == "rainy"
            assert updated_user.user_profile_picture == "new_profile.jpg"


def test_update_user_account_not_found(app):
    """Test updating non-existent user account"""
    test_data = {"user_name": "Updated Name"}

    with app.test_request_context(json=test_data):
        response, status_code = update_user_account(999)
        assert status_code == 404
        assert "not found" in response.json["message"]


def test_update_user_account_no_data(app):
    """Test updating user account with no data"""
    with app.app_context():
        # Create a test user
        user = UserAccount(
            user_username="testuser",
            user_password="password123",
            user_name="Test User",
            user_email="test@example.com",
            user_phone="1234567890",
            user_address="123 Test St",
            user_location="Test City",
            user_weather="sunny",
            user_profile_picture="profile.jpg",
        )
        db.session.add(user)
        db.session.commit()

        with app.test_request_context(json={}, content_type="application/json"):
            response, status_code = update_user_account(user.user_id)
            assert status_code == 400
            assert response.json["message"] == "Invalid input"


@patch("app.Controllers.userAccountController.UserAccount.query")
def test_update_user_account_db_error(mock_query, app):
    """Test updating user account with database error"""
    mock_query.filter_by.side_effect = SQLAlchemyError("Database error")

    with app.test_request_context(
        json={"user_name": "Updated Name"}, content_type="application/json"
    ):
        response, status_code = update_user_account(1)
        assert status_code == 500
        assert "Database error" in response.json["message"]


def test_delete_user_account_success(app):
    """Test successful user account deletion"""
    with app.app_context():
        # Create a test user
        user = UserAccount(
            user_username="testuser",
            user_password="password123",
            user_name="Test User",
            user_email="test@example.com",
            user_phone="1234567890",
            user_address="123 Test St",
            user_location="Test City",
            user_weather="sunny",
            user_profile_picture="profile.jpg",
        )
        db.session.add(user)
        db.session.commit()

        response, status_code = delete_user_account(user.user_id)
        assert status_code == 200
        assert response.json["message"] == "User account deleted"

        # Verify user is deleted
        assert db.session.get(UserAccount, user.user_id) is None


def test_delete_user_account_not_found(app):
    """Test deleting non-existent user account"""
    with app.app_context():
        response, status_code = delete_user_account(999)
        assert status_code == 404
        assert "not found" in response.json["message"]


@patch("app.Controllers.userAccountController.UserAccount.query")
def test_delete_user_account_db_error(mock_query, app):
    """Test deleting user account with database error"""
    mock_query.filter_by.side_effect = SQLAlchemyError("Database error")

    with app.app_context():
        response, status_code = delete_user_account(1)
        assert status_code == 500
        assert "Database error" in response.json["message"]
