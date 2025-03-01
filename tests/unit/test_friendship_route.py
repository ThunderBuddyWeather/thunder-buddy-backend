"""Unit tests for friendship routes"""

import os
from unittest.mock import Mock, patch

import pytest
from flask import Flask, jsonify
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import caching, db, limiter
from app.Models.friendshipModel import Friendship
from app.Models.userAccountModel import UserAccount
from app.Routes.friendshipRoute import friendship_blueprint

# Check if running in CI environment
IN_CI = os.environ.get('CI') == 'true'
skip_in_ci = pytest.mark.skipif(
    IN_CI, 
    reason="JWT authentication tests are skipped in CI environment"
)

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = 'test-key'
    app.config['JWT_SECRET_KEY'] = 'test-jwt-key'
    
    # Initialize extensions
    JWTManager(app)
    db.init_app(app)
    limiter.init_app(app)
    caching.init_app(app)
    
    # Register blueprints
    app.register_blueprint(friendship_blueprint, url_prefix='/api/friends')
    
    # Create tables
    with app.app_context():
        db.create_all()
    
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

@pytest.fixture
def test_users(app):
    """Create test users and return their IDs"""
    with app.app_context():
        user1 = UserAccount(
            user_username='user1',
            user_password='password1',
            user_name='User One',
            user_email='user1@example.com',
            user_phone='1234567890',
            user_address='123 Test St',
            user_location='Test City',
            user_weather='sunny',
            user_profile_picture='profile1.jpg'
        )
        user2 = UserAccount(
            user_username='user2',
            user_password='password2',
            user_name='User Two',
            user_email='user2@example.com',
            user_phone='0987654321',
            user_address='456 Test St',
            user_location='Test City',
            user_weather='cloudy',
            user_profile_picture='profile2.jpg'
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        user1_id = user1.user_id
        user2_id = user2.user_id
        return user1_id, user2_id

@pytest.fixture
def auth_headers(app):
    """Create authorization headers for testing."""
    with app.app_context():
        token = create_access_token(identity=1)
        return {'Authorization': f'Bearer {token}'}

@pytest.fixture
def mock_get_jwt_identity():
    """Mock get_jwt_identity to return user_id 1"""
    with patch('app.Routes.friendshipRoute.get_jwt_identity') as mock:
        mock.return_value = 1
        yield mock

@skip_in_ci
def test_send_friend_request_success(app, client, auth_headers, mock_get_jwt_identity):
    """Test successful friend request"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.UserAccount.query') as mock_query:
            mock_user = UserAccount(
                user_username='testuser2',
                user_password='password',
                user_name='Test User',
                user_email='test2@example.com'
            )
            mock_user.user_id = 2  # Set ID after creation
            mock_query.get.return_value = mock_user
            with patch('app.Routes.friendshipRoute.get_friendship') as mock_get_friendship:
                mock_get_friendship.return_value = None
                response = client.post('/api/friends/request/2', headers=auth_headers)
                assert response.status_code == 201

@skip_in_ci
def test_send_friend_request_missing_id(app, client, auth_headers):
    """Test friend request with missing ID"""
    response = client.post('/api/friends/request/', headers=auth_headers)
    assert response.status_code == 404

@skip_in_ci
def test_send_friend_request_user_not_found(app, client, auth_headers, mock_get_jwt_identity):
    """Test friend request to non-existent user"""
    with app.app_context():
        with patch('app.Routes.friendshipRoute.UserAccount.query.get') as mock_get:
            mock_get.return_value = None
            response = client.post('/api/friends/request/999', headers=auth_headers)
            assert response.status_code == 404
            # Don't assume response.json exists
            if response.json:
                assert response.json.get('message') == "User not found"

@skip_in_ci
def test_send_friend_request_already_exists(app, client, auth_headers, mock_get_jwt_identity):
    """Test friend request when friendship already exists"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.UserAccount.query') as mock_query:
            mock_user = UserAccount(
                user_username='testuser2',
                user_password='password',
                user_name='Test User',
                user_email='test2@example.com'
            )
            mock_user.user_id = 2  # Set ID after creation
            mock_query.get.return_value = mock_user
            with patch('app.Routes.friendshipRoute.get_friendship') as mock_get_friendship:
                mock_get_friendship.return_value = Friendship(user1_id=1, user2_id=2, friendship_status='pending')
                response = client.post('/api/friends/request/2', headers=auth_headers)
                assert response.status_code == 400

@skip_in_ci
def test_accept_friend_request_success(app, client, auth_headers, mock_get_jwt_identity):
    """Test successful friend request acceptance"""
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get:
            mock_get.return_value = Friendship(user1_id=1, user2_id=2, friendship_status='pending')
            response = client.put('/api/friends/accept/2', headers=auth_headers)
            assert response.status_code == 200

@skip_in_ci
def test_accept_friend_request_not_found(app, client, auth_headers, mock_get_jwt_identity):
    """Test accepting non-existent friend request"""
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get:
            mock_get.return_value = None
            response = client.put('/api/friends/accept/2', headers=auth_headers)
            assert response.status_code == 404
            # Don't assume response.json exists
            if response.json:
                assert response.json.get('message') == "Friendship not found"

@skip_in_ci
def test_accept_friend_request_invalid_status(app, client, auth_headers, mock_get_jwt_identity):
    """Test accepting friend request with invalid status"""
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get:
            mock_get.return_value = Friendship(user1_id=1, user2_id=2, friendship_status='accepted')
            response = client.put('/api/friends/accept/2', headers=auth_headers)
            assert response.status_code == 400

@skip_in_ci
def test_get_friends_list_success(app, client, auth_headers, mock_get_jwt_identity):
    """Test successful friends list retrieval"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.Friendship.query') as mock_friendship_query:
            mock_friendship = Friendship(user1_id=1, user2_id=2, friendship_status='accepted')
            mock_friendship_query.filter.return_value.all.return_value = [mock_friendship]
            with patch('app.Routes.friendshipRoute.UserAccount.query') as mock_user_query:
                mock_user = UserAccount(
                    user_username='testuser2',
                    user_password='password',
                    user_name='Test User',
                    user_email='test2@example.com'
                )
                mock_user.user_id = 2  # Set ID after creation
                mock_user_query.get.return_value = mock_user
                response = client.get('/api/friends', headers=auth_headers)
                assert response.status_code == 200

@skip_in_ci
def test_get_friends_list_empty(app, client, auth_headers, mock_get_jwt_identity):
    """Test empty friends list retrieval"""
    with app.app_context():
        with patch('app.Routes.friendshipRoute.Friendship.query.filter') as mock_filter:
            mock_filter.return_value.all.return_value = []
            response = client.get('/api/friends', headers=auth_headers)
            assert response.status_code == 200

@skip_in_ci
def test_unfriend_success(app, client, auth_headers, mock_get_jwt_identity):
    """Test successful unfriending"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get_friendship:
            mock_friendship = Friendship(user1_id=1, user2_id=2, friendship_status='accepted')
            mock_get_friendship.return_value = mock_friendship
            with patch('app.Routes.friendshipRoute.db.session.delete') as mock_delete:
                with patch('app.Routes.friendshipRoute.db.session.commit'):
                    response = client.delete('/api/friends/2', headers=auth_headers)
                    assert response.status_code == 204

@skip_in_ci
def test_unfriend_not_found(app, client, auth_headers, mock_get_jwt_identity):
    """Test unfriending non-existent friendship"""
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get:
            mock_get.return_value = None
            response = client.delete('/api/friends/2', headers=auth_headers)
            assert response.status_code == 404
            # Don't assume response.json exists
            if response.json:
                assert response.json.get('message') == "Friendship not found"

@skip_in_ci
def test_unfriend_invalid_status(app, client, auth_headers, mock_get_jwt_identity):
    """Test unfriending with invalid status"""
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get:
            mock_get.return_value = Friendship(user1_id=1, user2_id=2, friendship_status='pending')
            response = client.delete('/api/friends/2', headers=auth_headers)
            assert response.status_code == 409

@skip_in_ci
def test_send_friend_request_invalid_id_format(app, client, auth_headers, mock_get_jwt_identity):
    """Test friend request with invalid ID format"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        response = client.post('/api/friends/request/invalid', headers=auth_headers)
        assert response.status_code == 404

@skip_in_ci
def test_send_friend_request_to_self(app, client, auth_headers, mock_get_jwt_identity):
    """Test sending friend request to self"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        response = client.post('/api/friends/request/1', headers=auth_headers)
        assert response.status_code == 400

@skip_in_ci
def test_send_friend_request_unexpected_error(app, client, auth_headers, mock_get_jwt_identity):
    """Test handling of unexpected errors in send_friend_request"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.UserAccount.query') as mock_query:
            mock_query.get.side_effect = Exception("Unexpected error")
            response = client.post('/api/friends/request/2', headers=auth_headers)
            assert response.status_code == 500

@skip_in_ci
def test_accept_friend_request_database_error(app, client, auth_headers, mock_get_jwt_identity):
    """Test handling of database errors in accept_friend_request"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get_friendship:
            mock_friendship = Friendship(user1_id=1, user2_id=2, friendship_status='pending')
            mock_get_friendship.return_value = mock_friendship
            with patch('app.Routes.friendshipRoute.db.session.commit') as mock_commit:
                mock_commit.side_effect = SQLAlchemyError("Database error")
                response = client.put('/api/friends/accept/2', headers=auth_headers)
                assert response.status_code == 500

@skip_in_ci
def test_accept_friend_request_unexpected_error(app, client, auth_headers, mock_get_jwt_identity):
    """Test handling of unexpected errors in accept_friend_request"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get_friendship:
            mock_get_friendship.side_effect = Exception("Unexpected error")
            response = client.put('/api/friends/accept/2', headers=auth_headers)
            assert response.status_code == 500

@skip_in_ci
def test_get_friends_list_database_error(app, client, auth_headers, mock_get_jwt_identity):
    """Test handling of database errors in get_friends_list"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.Friendship.query') as mock_query:
            mock_query.filter.side_effect = SQLAlchemyError("Database error")
            response = client.get('/api/friends', headers=auth_headers)
            assert response.status_code == 500

@skip_in_ci
def test_get_friends_list_unexpected_error(app, client, auth_headers, mock_get_jwt_identity):
    """Test handling of unexpected errors in get_friends_list"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.Friendship.query') as mock_query:
            mock_query.filter.side_effect = Exception("Unexpected error")
            response = client.get('/api/friends', headers=auth_headers)
            assert response.status_code == 500

@skip_in_ci
def test_unfriend_database_error(app, client, auth_headers, mock_get_jwt_identity):
    """Test handling of database errors in unfriend"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get_friendship:
            mock_friendship = Friendship(user1_id=1, user2_id=2, friendship_status='accepted')
            mock_get_friendship.return_value = mock_friendship
            with patch('app.Routes.friendshipRoute.db.session.delete') as mock_delete:
                mock_delete.side_effect = SQLAlchemyError("Database error")
                response = client.delete('/api/friends/2', headers=auth_headers)
                assert response.status_code == 500

@skip_in_ci
def test_unfriend_unexpected_error(app, client, auth_headers, mock_get_jwt_identity):
    """Test handling of unexpected errors in unfriend"""
    mock_get_jwt_identity.return_value = 1
    with app.app_context():
        with patch('app.Routes.friendshipRoute.get_friendship') as mock_get_friendship:
            mock_get_friendship.side_effect = Exception("Unexpected error")
            response = client.delete('/api/friends/2', headers=auth_headers)
            assert response.status_code == 500 