"""Unit tests for main Flask application"""

from unittest.mock import Mock, patch

import pytest
import requests
from faker import Faker

from main import app

# Initialize Faker
fake = Faker()


@pytest.fixture
def client():
    """Create a test client for the Flask app"""
    with app.test_client() as client:
        yield client


@pytest.mark.unit
def test_hello_world(client):
    """Test the root endpoint returns expected greeting"""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json == {"Message": "Hello World"}


@pytest.mark.unit
class TestWeatherEndpoint:
    """Test cases for the /weather endpoint"""

    def test_get_weather_success(self, client):
        """Test successful weather data retrieval"""
        # Mock weather API response
        mock_weather_data = {
            "data": [
                {
                    "temp": fake.pyfloat(min_value=-10, max_value=100),
                    "city_name": fake.city(),
                    "weather": {"description": fake.text(max_nb_chars=20)},
                }
            ]
        }

        with patch("requests.get") as mock_get:
            # Configure mock
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = mock_weather_data
            mock_get.return_value = mock_response

            # Make request
            response = client.get("/weather?zip=12345&country=US")

            # Assertions
            assert response.status_code == 200
            assert response.json == mock_weather_data
            mock_get.assert_called_once()

    def test_get_weather_default_params(self, client):
        """Test weather endpoint with default parameters"""
        with patch("requests.get") as mock_get:
            # Configure mock
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            mock_get.return_value = mock_response

            # Make request without parameters
            response = client.get("/weather")

            # Verify default parameters
            mock_get.assert_called_once()
            args = mock_get.call_args[1]["params"]
            assert args["postal_code"] == "30152"  # Default ZIP
            assert args["country"] == "US"  # Default country
            assert response.status_code == 200

    def test_get_weather_missing_zip(self, client):
        """Test weather endpoint with empty ZIP code"""
        response = client.get("/weather?zip=")
        assert response.status_code == 400
        assert response.json == {"error": "ZIP code is required"}

    def test_get_weather_api_error(self, client):
        """Test handling of WeatherBit API errors"""
        with patch("requests.get") as mock_get:
            # Configure mock for API error
            mock_response = Mock()
            mock_response.status_code = 403
            mock_response.json.return_value = {"error": "API key invalid"}
            mock_get.return_value = mock_response

            # Make request
            response = client.get("/weather?zip=12345")

            # Verify error handling
            assert response.status_code == 403
            assert response.get_json() == {"error": "Failed to fetch weather data"}

    def test_get_weather_timeout(self, client):
        """Test handling of timeout errors"""
        with patch(
            "requests.get", side_effect=requests.exceptions.Timeout("Request timed out")
        ):
            response = client.get("/weather?zip=12345")
            assert response.status_code == 500
            assert response.get_json() == {"error": "Request timed out"}

    def test_get_weather_request_exception(self, client):
        """Test handling of general request exceptions"""
        with patch(
            "requests.get",
            side_effect=requests.exceptions.RequestException("Network error"),
        ):
            response = client.get("/weather?zip=12345")
            assert response.status_code == 500
            assert response.get_json() == {"error": "API request failed"}

    def test_get_weather_invalid_json(self, client):
        """Test handling of invalid JSON responses"""
        with patch("requests.get") as mock_get:
            # Configure mock to return invalid JSON
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.side_effect = ValueError("Invalid JSON")
            mock_get.return_value = mock_response

            response = client.get("/weather?zip=12345")
            assert response.status_code == 500
            assert response.get_json() == {"error": "Invalid response format"}

    @pytest.mark.parametrize(
        "zip_code,country", [("12345", "GB"), ("54321", "DE"), ("98765", "FR")]
    )
    def test_get_weather_different_countries(self, client, zip_code, country):
        """Test weather endpoint with different country codes"""
        with patch("requests.get") as mock_get:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"data": []}
            mock_get.return_value = mock_response

            response = client.get(f"/weather?zip={zip_code}&country={country}")

            assert response.status_code == 200
            args = mock_get.call_args[1]["params"]
            assert args["postal_code"] == zip_code
            assert args["country"] == country
