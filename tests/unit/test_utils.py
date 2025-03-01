"""Unit tests for utility functions"""

import os
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from flask import Flask, jsonify

from app.utils import encode_token, get_remote_address, token_required

TEST_SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    app = Flask(__name__)
    app.config['SECRET_KEY'] = TEST_SECRET_KEY
    return app

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_encode_token(app):
    """Test token encoding"""
    with app.app_context():
        user_id = 123
        token = encode_token(user_id)
        assert isinstance(token, str)
        # Decode and verify token
        payload = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        assert payload['sub'] == user_id

def test_token_required_valid_token(app, client):
    """Test token_required decorator with valid token"""
    with app.app_context():
        user_id = 123
        token = encode_token(user_id)

        @app.route('/test')
        @token_required
        def test_route():
            return jsonify({'message': 'success'}), 200

        response = client.get('/test', headers={'Authorization': f'Bearer {token}'})
        assert response.status_code == 200
        assert response.json['message'] == 'success'

def test_token_required_missing_token(app, client):
    """Test token_required decorator with missing token"""
    @app.route('/test')
    @token_required
    def test_route():
        return jsonify({'message': 'success'}), 200

    response = client.get('/test')
    assert response.status_code == 401
    assert 'Token is missing' in response.json['message']

def test_token_required_invalid_token(app, client):
    """Test token_required decorator with invalid token"""
    @app.route('/test')
    @token_required
    def test_route():
        return jsonify({'message': 'success'}), 200

    response = client.get('/test', headers={'Authorization': 'Bearer invalid_token'})
    assert response.status_code == 401
    assert 'Token is invalid' in response.json['message']

def test_token_required_expired_token(app, client):
    """Test token_required decorator with expired token"""
    with app.app_context():
        # Create an expired token
        payload = {
            'exp': datetime.now(timezone.utc) - timedelta(hours=1),
            'iat': datetime.now(timezone.utc) - timedelta(hours=2),
            'sub': 123
        }
        expired_token = jwt.encode(payload, app.config['SECRET_KEY'], algorithm='HS256')

        @app.route('/test')
        @token_required
        def test_route():
            return jsonify({'message': 'success'}), 200

        response = client.get('/test', headers={'Authorization': f'Bearer {expired_token}'})
        assert response.status_code == 401
        assert 'Token has expired' in response.json['message']

def test_get_remote_address(app):
    """Test getting remote address"""
    with app.test_request_context():
        address = get_remote_address()
        assert address == '127.0.0.1' 