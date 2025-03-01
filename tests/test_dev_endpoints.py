"""
Tests for development-only endpoints
Verifies that development endpoints are only available in development mode
"""

import json
import unittest
from unittest.mock import patch

from app import create_app
from app.Models.userAccountModel import UserAccount


class TestDevEndpoints(unittest.TestCase):
    """Test cases for development endpoints"""

    def setUp(self):
        """Set up the test environment"""
        # Create a development app instance
        self.dev_app = create_app("development")
        self.dev_client = self.dev_app.test_client()
        
        # Create a production app instance
        self.prod_app = create_app("production")
        self.prod_client = self.prod_app.test_client()
        
        # Set up the test environment for both apps
        with self.dev_app.app_context():
            # In development mode, database setup happens automatically
            pass
            
        with self.prod_app.app_context():
            # In production mode, database setup happens automatically
            pass

    def test_health_endpoint_in_dev_mode(self):
        """Test that health endpoint works in development mode"""
        # Make request to the health endpoint
        response = self.dev_client.get('/dev/health')
        
        # Check that the response is successful
        self.assertEqual(response.status_code, 200)
        
        # Parse the response data
        data = json.loads(response.data)
        
        # Check the response contains expected fields
        self.assertEqual(data['status'], 'ok')
        self.assertEqual(data['environment'], 'development')

    def test_health_endpoint_in_prod_mode(self):
        """Test that health endpoint is not available in production mode"""
        # Make request to the health endpoint in production mode
        response = self.prod_client.get('/dev/health')
        
        # Check that the endpoint is not found (404) in production
        self.assertEqual(response.status_code, 404)

    def test_users_endpoint_in_dev_mode(self):
        """Test that users endpoint works in development mode"""
        # Mock the database query to return a list of users
        with patch.object(UserAccount, 'query') as mock_query:
            # Set up the mock to return a mock user list
            mock_users = []
            mock_query.all.return_value = mock_users
            
            # Make request to the users endpoint
            response = self.dev_client.get('/dev/users')
            
            # Check that the response is successful
            self.assertEqual(response.status_code, 200)
            
            # Parse the response data
            data = json.loads(response.data)
            
            # Check the response contains expected fields
            self.assertIn('users', data)
            self.assertIn('count', data)
            self.assertEqual(data['environment'], 'development')
            
            # Verify the query was called
            mock_query.all.assert_called_once()

    def test_users_endpoint_in_prod_mode(self):
        """Test that users endpoint is not available in production mode"""
        # Make request to the users endpoint in production mode
        response = self.prod_client.get('/dev/users')
        
        # Check that the endpoint is not found (404) in production
        self.assertEqual(response.status_code, 404)


if __name__ == '__main__':
    unittest.main() 