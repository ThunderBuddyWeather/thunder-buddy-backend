import os
from typing import Any, Dict

import pytest
from dotenv import load_dotenv
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.extensions import db

# Load test environment variables
load_dotenv('.env.test')

class BaseTestCase:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Set up test environment before each test"""
        # Create app with test config
        self.app = create_app("testing")
        self.app.config["TESTING"] = True
        
        # Create test client
        self.client = self.app.test_client()
        
        # Create all tables
        with self.app.app_context():
            db.drop_all()  # Clean up any existing tables
            db.create_all()
        
        yield
        
        # Clean up after test
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def create_test_user(self, email: str = "test@example.com", password: str = "password123") -> Dict[str, Any]:
        """Helper to create a test user and return their data"""
        response = self.client.post("/api/user/register", json={
            "email": email,
            "password": password,
            "name": "Test User"
        })
        return response.get_json()

    def login_test_user(self, email: str = "test@example.com", password: str = "password123") -> str:
        """Helper to login a test user and return their access token"""
        response = self.client.post("/api/user/login", json={
            "email": email,
            "password": password
        })
        return response.get_json()["access_token"]

    def get_auth_headers(self, token: str) -> Dict[str, str]:
        """Helper to create authorization headers"""
        return {"Authorization": f"Bearer {token}"} 