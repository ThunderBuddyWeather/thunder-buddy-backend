import pytest

from app import create_app
from app.extensions import db
from app.Models.friendshipModel import Friendship

from .test_base import BaseTestCase


class TestFriendship:
    """Test friendship functionality"""

    def setup_method(self):
        """Set up test client and users"""
        self.app = create_app("testing")
        self.client = self.app.test_client()

        # Create test users
        self.user1 = {
            "email": "test1@example.com",
            "password": "password123",
            "name": "Test User 1",
            "username": "testuser1",
        }
        response = self.client.post("/api/user/register", json=self.user1)
        # Handle either a successful registration (201) or existing user (400)
        if response.status_code == 201:
            self.user1["user_id"] = response.json["user_id"]
        else:
            # User already exists, get their ID by logging in
            login_response = self.client.post(
                "/api/user/login",
                json={"email": self.user1["email"], "password": self.user1["password"]},
            )
            # Get profile to retrieve ID
            profile_response = self.client.get(
                "/api/user/profile",
                headers={
                    "Authorization": f'Bearer {login_response.json["access_token"]}'
                },
            )
            self.user1["user_id"] = profile_response.json["user_id"]

        self.user2 = {
            "email": "test2@example.com",
            "password": "password123",
            "name": "Test User 2",
            "username": "testuser2",
        }
        response = self.client.post("/api/user/register", json=self.user2)
        # Handle either a successful registration (201) or existing user (400)
        if response.status_code == 201:
            self.user2["user_id"] = response.json["user_id"]
        else:
            # User already exists, get their ID by logging in
            login_response = self.client.post(
                "/api/user/login",
                json={"email": self.user2["email"], "password": self.user2["password"]},
            )
            # Get profile to retrieve ID
            profile_response = self.client.get(
                "/api/user/profile",
                headers={
                    "Authorization": f'Bearer {login_response.json["access_token"]}'
                },
            )
            self.user2["user_id"] = profile_response.json["user_id"]

        # Get tokens
        response = self.client.post(
            "/api/user/login",
            json={"email": self.user1["email"], "password": self.user1["password"]},
        )
        self.token1 = response.json["access_token"]

        response = self.client.post(
            "/api/user/login",
            json={"email": self.user2["email"], "password": self.user2["password"]},
        )
        self.token2 = response.json["access_token"]

    def get_auth_headers(self, user):
        """Helper to get auth headers for a user"""
        response = self.client.post(
            "/api/user/login",
            json={"email": user["email"], "password": user["password"]},
        )
        token = response.json["access_token"]
        return {"Authorization": f"Bearer {token}"}

    def test_send_friend_request(self):
        """Test sending friend request"""
        response = self.client.post(
            f'/api/friends/request/{self.user2["user_id"]}',
            headers=self.get_auth_headers(self.user1),
        )
        assert response.status_code == 201

    def test_accept_friend_request(self):
        """Test accepting friend request"""
        # Send request first
        self.client.post(
            f'/api/friends/request/{self.user2["user_id"]}',
            headers=self.get_auth_headers(self.user1),
        )

        # Accept request
        response = self.client.put(
            f'/api/friends/accept/{self.user1["user_id"]}',
            headers=self.get_auth_headers(self.user2),
        )
        assert response.status_code == 200

    def test_reject_friend_request(self):
        """Test rejecting friend request"""
        # Create unique users for this test to avoid state pollution
        temp_user1 = {
            "email": "tempreject1@example.com",
            "password": "password123",
            "name": "Temp Reject User 1",
            "username": "tempreject1",
        }
        temp_user1_resp = self.client.post("/api/user/register", json=temp_user1)
        temp_user1["user_id"] = temp_user1_resp.json["user_id"]

        temp_user2 = {
            "email": "tempreject2@example.com",
            "password": "password123",
            "name": "Temp Reject User 2",
            "username": "tempreject2",
        }
        temp_user2_resp = self.client.post("/api/user/register", json=temp_user2)
        temp_user2["user_id"] = temp_user2_resp.json["user_id"]

        # Send request first - user1 sends request to user2
        self.client.post(
            f'/api/friends/request/{temp_user2["user_id"]}',
            headers=self.get_auth_headers(temp_user1),
        )

        # Reject request - user2 rejects user1's request
        response = self.client.put(
            f'/api/friends/reject/{temp_user1["user_id"]}',
            headers=self.get_auth_headers(temp_user2),
        )

        # For debugging purposes
        print(f"Response status: {response.status_code}")

        # With 204 status, there is no JSON content to check
        assert response.status_code == 204  # Successfully rejected

    def test_reject_friend_request_wrong_status(self):
        """Test rejecting friendship that's not in pending state"""
        # Create unique users for this test to avoid state pollution
        temp_user1 = {
            "email": "temp1@example.com",
            "password": "password123",
            "name": "Temp User 1",
            "username": "tempuser1",
        }
        temp_user1_resp = self.client.post("/api/user/register", json=temp_user1)
        temp_user1["user_id"] = temp_user1_resp.json["user_id"]

        temp_user2 = {
            "email": "temp2@example.com",
            "password": "password123",
            "name": "Temp User 2",
            "username": "tempuser2",
        }
        temp_user2_resp = self.client.post("/api/user/register", json=temp_user2)
        temp_user2["user_id"] = temp_user2_resp.json["user_id"]

        # Send request
        self.client.post(
            f'/api/friends/request/{temp_user2["user_id"]}',
            headers=self.get_auth_headers(temp_user1),
        )

        # Accept request
        self.client.put(
            f'/api/friends/accept/{temp_user1["user_id"]}',
            headers=self.get_auth_headers(temp_user2),
        )

        # Try to reject an already accepted request
        response = self.client.put(
            f'/api/friends/reject/{temp_user1["user_id"]}',
            headers=self.get_auth_headers(temp_user2),
        )
        assert response.status_code == 409  # Conflict, can't reject accepted friendship

    def test_get_friends_list(self):
        """Test getting friends list"""
        # Create friendship first
        self.client.post(
            f'/api/friends/request/{self.user2["user_id"]}',
            headers=self.get_auth_headers(self.user1),
        )
        self.client.put(
            f'/api/friends/accept/{self.user1["user_id"]}',
            headers=self.get_auth_headers(self.user2),
        )

        # Get friends list
        response = self.client.get(
            "/api/friends", headers=self.get_auth_headers(self.user1)
        )
        assert response.status_code == 200
        assert len(response.json["friends"]) == 1
        assert response.json["friends"][0]["user_id"] == 2  # The user2 ID is 2

    def test_unfriend(self):
        """Test unfriending"""
        # Create unique users for this test to avoid state pollution
        temp_user1 = {
            "email": "tempunfriend1@example.com",
            "password": "password123",
            "name": "Temp Unfriend User 1",
            "username": "tempunfriend1",
        }
        temp_user1_resp = self.client.post("/api/user/register", json=temp_user1)
        temp_user1["user_id"] = temp_user1_resp.json["user_id"]

        temp_user2 = {
            "email": "tempunfriend2@example.com",
            "password": "password123",
            "name": "Temp Unfriend User 2",
            "username": "tempunfriend2",
        }
        temp_user2_resp = self.client.post("/api/user/register", json=temp_user2)
        temp_user2["user_id"] = temp_user2_resp.json["user_id"]

        # Send friend request
        response = self.client.post(
            f'/api/friends/request/{temp_user2["user_id"]}',
            headers=self.get_auth_headers(temp_user1),
        )
        assert response.status_code == 201

        # Accept friend request
        response = self.client.put(
            f'/api/friends/accept/{temp_user1["user_id"]}',
            headers=self.get_auth_headers(temp_user2),
        )
        assert response.status_code == 200

        # Verify friendship exists
        response = self.client.get(
            "/api/friends", headers=self.get_auth_headers(temp_user1)
        )
        assert response.status_code == 200
        assert len(response.json["friends"]) == 1

        # Unfriend
        response = self.client.delete(
            f'/api/friends/{temp_user2["user_id"]}',
            headers=self.get_auth_headers(temp_user1),
        )
        assert response.status_code == 204  # Successfully unfriended

        # Verify friendship is removed
        response = self.client.get(
            "/api/friends", headers=self.get_auth_headers(temp_user1)
        )
        assert response.status_code == 200
        assert len(response.json["friends"]) == 0

    def test_unfriend_not_found(self):
        """Test unfriending non-existent friendship"""
        # Try to unfriend without creating friendship first
        response = self.client.delete(
            f'/api/friends/{self.user2["user_id"]}',
            headers=self.get_auth_headers(self.user1),
        )
        assert response.status_code == 404  # Friendship not found
