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
from flask import Flask, jsonify, redirect, request, send_from_directory
from flask_swagger_ui import get_swaggerui_blueprint
from sqlalchemy import create_engine, text

from scripts.test_db_connection import test_connection

# Load environment variables from .env.local if it exists
env_path = os.path.join(os.path.dirname(__file__), ".env.local")
if os.path.exists(env_path):
    load_dotenv(env_path)
else:
    load_dotenv()  # fallback to .env

app = Flask(__name__, static_url_path="", static_folder="static")

# Configure Swagger UI
SWAGGER_URL = "/apidocs/"
API_URL = "/static/swagger.yaml"

swaggerui_blueprint = get_swaggerui_blueprint(
    base_url=SWAGGER_URL,
    api_url=API_URL,
    config={
        "app_name": "Thunder Buddy API",
        "validatorUrl": None,
        "layout": "BaseLayout",
        "deepLinking": True,
    },
)

# Register blueprint with URL rule handling
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)


# Serve swagger spec
@app.route("/static/swagger.yaml")
def serve_swagger_spec():
    """Serve the Swagger specification file"""
    return send_from_directory("static", "swagger.yaml")


# Add a redirect for the base /apidocs URL
@app.route("/apidocs")
def swagger_ui():
    """Redirect to Swagger UI"""
    return redirect("/apidocs/")


# fmt: off
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY",
                               "d0f6ba4e6ca24b08a0896b004a08b2ac")  # noqa: E501
timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))  # Default as string "10"
# fmt: on

# Configure logging
logging.basicConfig(level=logging.ERROR)


@app.route("/", methods=["GET"])
def hello_world():
    """
    Get a simple greeting message
    ---
    get:
        summary: Get greeting message
        description: Returns a simple hello world message
        responses:
            200:
                description: Successful response
                content:
                    application/json:
                        schema:
                            type: object
                            properties:
                                Message:
                                    type: string
                                    example: "Hello World"
    """
    return jsonify({"Message": "Hello World"}), 200


@app.route("/weather", methods=["GET"])
def get_local_weather():
    """
    Get current weather data for a given ZIP code and country
    ---
    get:
        summary: Get local weather
        description: Returns current weather data for the specified location
        parameters:
            - in: query
              name: zip
              schema:
                type: string
              description: ZIP/Postal code
              example: "30152"
              required: false
            - in: query
              name: country
              schema:
                type: string
              description: Country code
              example: "US"
              required: false
        responses:
            200:
                description: Successful weather data response
            400:
                description: Invalid parameters
            500:
                description: Server error or external API failure
    """
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
def health_check():
    """
    Check the health status of the application
    ---
    get:
        summary: Health check endpoint
        description: Verifies the health of the application and its components
        responses:
            200:
                description: Application is healthy
            503:
                description: Application is unhealthy
    """
    db_health: Dict[str, str] = check_db_health()

    health_status = {
        "status": (
            "healthy"
            if db_health["connection"] == "healthy" and db_health["query"] == "healthy"
            else "unhealthy"
        ),
        "components": {
            "api": {"status": "healthy", "message": "API service is running"},
            "database": db_health,
        },
    }

    http_status = 200 if health_status["status"] == "healthy" else 503
    return jsonify(health_status), http_status


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
