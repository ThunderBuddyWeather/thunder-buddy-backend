import pytest

from app.extensions import db
from app.Models.userAccountModel import UserAccount

from .test_base import BaseTestCase


class TestUserAccount(BaseTestCase):
    def test_register_user(self):
        """Test user registration"""
        response = self.client.post("/api/user/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Test User"
        })
        assert response.status_code == 201
        data = response.get_json()
        assert "user_id" in data
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert "password" not in data  # Password should not be returned

    def test_register_duplicate_email(self):
        """Test registering with an existing email"""
        # Create first user
        self.create_test_user()
        
        # Try to create second user with same email
        response = self.client.post("/api/user/register", json={
            "email": "test@example.com",
            "password": "different123",
            "name": "Another User"
        })
        assert response.status_code == 400
        assert "already exists" in response.get_json()["message"].lower()

    def test_login_user(self):
        """Test user login"""
        # Create user
        self.create_test_user()
        
        # Login
        response = self.client.post("/api/user/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 200
        data = response.get_json()
        assert "access_token" in data

    def test_login_invalid_credentials(self):
        """Test login with wrong password"""
        # Create user
        self.create_test_user()
        
        # Try to login with wrong password
        response = self.client.post("/api/user/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        assert response.status_code == 401

    def test_get_user_profile(self):
        """Test getting user profile"""
        # Create and login user
        self.create_test_user()
        token = self.login_test_user()
        
        # Get profile
        response = self.client.get("/api/user/profile", headers=self.get_auth_headers(token))
        assert response.status_code == 200
        data = response.get_json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"

    def test_update_user_profile(self):
        """Test updating user profile"""
        # Create and login user
        self.create_test_user()
        token = self.login_test_user()
        
        # Update profile
        response = self.client.put("/api/user/profile", 
            headers=self.get_auth_headers(token),
            json={"name": "Updated Name"}
        )
        assert response.status_code == 204
        
        # Verify in database
        with self.app.app_context():
            user = UserAccount.query.filter_by(user_email="test@example.com").first()
            assert user.user_name == "Updated Name"

    def test_delete_user_account(self):
        """Test deleting user account"""
        # Create and login user
        self.create_test_user()
        token = self.login_test_user()
        
        # Delete account
        response = self.client.delete("/api/user/profile", headers=self.get_auth_headers(token))
        assert response.status_code == 204
        
        # Verify user is deleted
        with self.app.app_context():
            user = UserAccount.query.filter_by(user_email="test@example.com").first()
            assert user is None
        
        # Try to login - should fail
        response = self.client.post("/api/user/login", json={
            "email": "test@example.com",
            "password": "password123"
        })
        assert response.status_code == 401 