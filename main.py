"""
Weather API service built with Flask
Provides current weather data through REST endpoints
"""

import logging
import os
from typing import Dict, Tuple

import psycopg2
import requests  # noqa: E402
from dotenv import load_dotenv
from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text

try:
    from flask_swagger_ui import get_swaggerui_blueprint
except ImportError:
    get_swaggerui_blueprint = None
    logging.warning("flask-swagger-ui not installed. API docs will not be available.")

# Swagger UI setup
SWAGGER_URL = "/apidocs"
API_URL = "/static/swagger.yaml"  # Ensure the YAML file is inside the 'static' folder

if get_swaggerui_blueprint:
    swaggerui_blueprint = get_swaggerui_blueprint(
        SWAGGER_URL, API_URL, config={"app_name": "Thunder Buddy API"}
    )

from scripts.test_db_connection import test_connection  # Add this line

app = Flask(__name__)

load_dotenv()

# fmt: off
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY",
                               "d0f6ba4e6ca24b08a0896b004a08b2ac")  # noqa: E501
timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))  # Default as string "10"
# fmt: on

# Configure logging
logging.basicConfig(level=logging.ERROR)


@app.route("/", methods=["GET"])
def hello_world():
    """Return a simple greeting message"""
    return jsonify({"Message": "Hello World"}), 200


@app.route("/weather", methods=["GET"])
def get_local_weather():
    """Return current weather data for a given ZIP code and country"""
    zip_code = request.args.get("zip", "30152")  # Default to 30152
    country = request.args.get("country", "US")  # Default to US

    if not zip_code:
        return jsonify({"error": "ZIP code is required"}), 400

    weatherbit_url = "https://api.weatherbit.io/v2.0/current"
    params = {
        "postal_code": zip_code,
        "country": country,
        "units": "I",  # "I" for Fahrenheit, "M" for Celsius (default)
        "key": WEATHERBIT_API_KEY,
    }

    try:
        response = requests.get(weatherbit_url, params=params, timeout=timeout)

        # Handle non-200 status codes
        if response.status_code != 200:
            return (
                jsonify({"error": "Failed to fetch weather data"}),
                response.status_code,
            )

        try:
            return jsonify(response.json())
        except ValueError:  # This catches JSON decode errors
            return jsonify({"error": "Invalid response format"}), 500

    except requests.exceptions.Timeout:
        return jsonify({"error": "Request timed out"}), 500
    except requests.exceptions.RequestException:
        return jsonify({"error": "API request failed"}), 500


def check_db_health() -> Dict[str, str]:
    """
    Perform comprehensive database health checks
    Returns: Dictionary with connection and query status
    """
    return test_connection()


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Dict, int]:
    """Check the health of the application by verifying database connectivity."""
    db_health: Dict[str, str] = check_db_health()

    health_status = {
        "status": "healthy" 
        if db_health["connection"] == "healthy" and db_health["query"] == "healthy"
        else "unhealthy",
        "components": {
            "api": {
                "status": "healthy",
                "message": "API service is running"
            },
            "database": db_health
        }
    }

    http_status = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), http_status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
