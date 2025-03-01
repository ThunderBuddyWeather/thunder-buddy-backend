"""Unit tests for user account routes"""

import os
from unittest.mock import patch

import pytest
from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from app.extensions import caching, db, limiter
from app.Models.userAccountModel import UserAccount
from app.Routes.userAccountRoute import user_account_blueprint

# Check if running in CI environment
IN_CI = os.environ.get('CI') == 'true'
skip_in_ci = pytest.mark.skipif(
    IN_CI, 
    reason="JWT authentication tests are skipped in CI environment"
)

@pytest.fixture
def app():
    """Create a test Flask app"""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = 'test-secret-key'
    app.config['TESTING'] = True
    
    # Initialize extensions
    JWTManager(app)
    db.init_app(app)
    limiter.init_app(app)
    caching.init_app(app)
    
    # Register blueprint
    app.register_blueprint(user_account_blueprint, url_prefix='/api/user')
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create a test client"""
    return app.test_client()

@pytest.fixture
def test_user(app):
    """Create a test user and return their ID"""
    with app.app_context():
        user = UserAccount(
            user_username='testuser',
            user_password=generate_password_hash('password123'),
            user_name='Test User',
            user_email='test@example.com',
            user_phone='1234567890',
            user_address='123 Test St',
            user_location='Test City',
            user_weather='sunny',
            user_profile_picture='profile.jpg'
        )
        db.session.add(user)
        db.session.commit()
        return user.user_id

@pytest.fixture
def auth_headers(app):
    """Create authorization headers for testing"""
    def _auth_headers(user_id=1):
        with app.app_context():
            token = create_access_token(identity=user_id)
            return {'Authorization': f'Bearer {token}'}
    return _auth_headers

def test_register_success(client):
    """Test successful user registration"""
    response = client.post('/api/user/register', json={
        'email': 'new@example.com',
        'password': 'password123',
        'name': 'New User'
    })
    assert response.status_code == 201
    assert response.json['email'] == 'new@example.com'
    assert response.json['name'] == 'New User'

def test_register_missing_fields(client):
    """Test registration with missing fields"""
    response = client.post('/api/user/register', json={
        'email': 'new@example.com'
    })
    assert response.status_code == 400
    assert 'Missing required fields' in response.json['message']

def test_register_invalid_email(client):
    """Test registration with invalid email format"""
    response = client.post('/api/user/register', json={
        'email': 'invalid-email',
        'password': 'password123',
        'name': 'New User'
    })
    assert response.status_code == 400
    assert 'Invalid email format' in response.json['message']

def test_register_short_password(client):
    """Test registration with short password"""
    response = client.post('/api/user/register', json={
        'email': 'new@example.com',
        'password': '12345',
        'name': 'New User'
    })
    assert response.status_code == 400
    assert 'Password must be at least 6 characters long' in response.json['message']

def test_register_short_name(client):
    """Test registration with short name"""
    response = client.post('/api/user/register', json={
        'email': 'new@example.com',
        'password': 'password123',
        'name': 'A'
    })
    assert response.status_code == 400
    assert 'Name must be at least 2 characters long' in response.json['message']

def test_register_duplicate_email(client, test_user):
    """Test registration with existing email"""
    response = client.post('/api/user/register', json={
        'email': 'test@example.com',
        'password': 'password123',
        'name': 'New User'
    })
    assert response.status_code == 400
    assert 'Email already exists' in response.json['message']

def test_register_database_error(client, app):
    """Test registration with database error"""
    with app.app_context():
        with patch('app.Routes.userAccountRoute.db.session.commit') as mock_commit:
            mock_commit.side_effect = SQLAlchemyError("Database error")
            response = client.post('/api/user/register', json={
                'email': 'new@example.com',
                'password': 'password123',
                'name': 'New User'
            })
            assert response.status_code == 500
            assert 'Failed to create user account' in response.json['message']

def test_login_success(client, test_user):
    """Test successful login"""
    response = client.post('/api/user/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    assert response.status_code == 200
    assert 'access_token' in response.json

def test_login_missing_fields(client):
    """Test login with missing fields"""
    response = client.post('/api/user/login', json={
        'email': 'test@example.com'
    })
    assert response.status_code == 400
    assert 'Missing email or password' in response.json['message']

def test_login_invalid_credentials(client, test_user):
    """Test login with invalid credentials"""
    response = client.post('/api/user/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword'
    })
    assert response.status_code == 401
    assert 'Invalid email or password' in response.json['message']

def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post('/api/user/login', json={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    })
    assert response.status_code == 401
    assert 'Invalid email or password' in response.json['message']

def test_login_database_error(client, app):
    """Test login with database error"""
    with app.app_context():
        with patch('app.Routes.userAccountRoute.UserAccount.query') as mock_query:
            mock_query.filter_by.side_effect = SQLAlchemyError("Database error")
            response = client.post('/api/user/login', json={
                'email': 'test@example.com',
                'password': 'password123'
            })
            assert response.status_code == 500
            assert 'Internal server error' in response.json['message']

@skip_in_ci
def test_get_profile_success(client, test_user, auth_headers):
    """Test successful profile retrieval"""
    headers = auth_headers(test_user)
    response = client.get('/api/user/profile', headers=headers)
    assert response.status_code == 200
    assert response.json['email'] == 'test@example.com'
    assert response.json['name'] == 'Test User'

@skip_in_ci
def test_get_profile_not_found(client, auth_headers):
    """Test profile retrieval for non-existent user"""
    headers = auth_headers(999)
    response = client.get('/api/user/profile', headers=headers)
    assert response.status_code == 404
    assert 'User not found' in response.json['message']

@skip_in_ci
def test_get_profile_database_error(client, test_user, auth_headers):
    """Test profile retrieval with database error"""
    headers = auth_headers(test_user)
    with patch('app.Routes.userAccountRoute.db.session.get') as mock_get:
        mock_get.side_effect = SQLAlchemyError("Database error")
        response = client.get('/api/user/profile', headers=headers)
        assert response.status_code == 500
        assert 'Internal server error' in response.json['message']

@skip_in_ci
def test_update_profile_success(client, test_user, auth_headers):
    """Test successful profile update"""
    headers = auth_headers(test_user)
    response = client.put('/api/user/profile', headers=headers, json={
        'name': 'Updated Name',
        'phone': '9876543210'
    })
    assert response.status_code == 204

@skip_in_ci
def test_update_profile_not_found(client, auth_headers):
    """Test profile update for non-existent user"""
    headers = auth_headers(999)
    response = client.put('/api/user/profile', headers=headers, json={
        'name': 'Updated Name'
    })
    assert response.status_code == 404
    assert 'User not found' in response.json['message']

@skip_in_ci
def test_update_profile_no_data(client, test_user, auth_headers):
    """Test profile update with no data"""
    headers = auth_headers(test_user)
    response = client.put('/api/user/profile', headers=headers, json={})
    assert response.status_code == 400
    assert 'No data provided' in response.json['message']

@skip_in_ci
def test_update_profile_invalid_fields(client, test_user, auth_headers):
    """Test profile update with invalid fields"""
    headers = auth_headers(test_user)
    response = client.put('/api/user/profile', headers=headers, json={
        'invalid_field': 'value'
    })
    assert response.status_code == 400
    assert 'Invalid fields' in response.json['message']

@skip_in_ci
def test_update_profile_short_name(client, test_user, auth_headers):
    """Test profile update with short name"""
    headers = auth_headers(test_user)
    response = client.put('/api/user/profile', headers=headers, json={
        'name': 'A'
    })
    assert response.status_code == 400
    assert 'Name must be at least 2 characters long' in response.json['message']

@skip_in_ci
def test_update_profile_database_error(client, test_user, auth_headers):
    """Test profile update with database error"""
    headers = auth_headers(test_user)
    with patch('app.Routes.userAccountRoute.db.session.commit') as mock_commit:
        mock_commit.side_effect = SQLAlchemyError("Database error")
        response = client.put('/api/user/profile', headers=headers, json={
            'name': 'Updated Name'
        })
        assert response.status_code == 500
        assert 'Failed to update profile' in response.json['message']

@skip_in_ci
def test_delete_profile_success(client, test_user, auth_headers):
    """Test successful profile deletion"""
    headers = auth_headers(test_user)
    response = client.delete('/api/user/profile', headers=headers)
    assert response.status_code == 204

@skip_in_ci
def test_delete_profile_not_found(client, auth_headers):
    """Test profile deletion for non-existent user"""
    headers = auth_headers(999)
    response = client.delete('/api/user/profile', headers=headers)
    assert response.status_code == 404
    assert 'User not found' in response.json['message']

@skip_in_ci
def test_delete_profile_database_error(client, test_user, auth_headers):
    """Test profile deletion with database error"""
    headers = auth_headers(test_user)
    with patch('app.Routes.userAccountRoute.db.session.commit') as mock_commit:
        mock_commit.side_effect = SQLAlchemyError("Database error")
        response = client.delete('/api/user/profile', headers=headers)
        assert response.status_code == 500
        assert 'Failed to delete profile' in response.json['message']

def test_unauthorized_access(client):
    """Test accessing protected routes without token"""
    response = client.get('/api/user/profile')
    assert response.status_code == 401
    assert 'Missing Authorization Header' in response.json['msg']

def test_rate_limit_exceeded(client):
    """Test rate limiting"""
    for _ in range(11):  # Limit is 10 per minute
        response = client.post('/api/user/login', json={
            'email': 'test@example.com',
            'password': 'password123'
        })
    assert response.status_code == 429 