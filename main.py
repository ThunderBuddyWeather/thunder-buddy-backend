"""
Weather API service built with Flask
Provides current weather data through REST endpoints
"""

import logging
import os
from typing import Dict, Tuple

import requests  # noqa: E402
from dotenv import load_dotenv
from flask import Flask, jsonify, request

# Import our database module
from scripts.db import init_db
from scripts.db import test_connection as check_db_health

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

app = Flask(__name__)

# Register Swagger UI blueprint if available
if get_swaggerui_blueprint:
    app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

# Try to load from .env.local first, then fall back to .env
if os.path.exists(".env.local"):
    load_dotenv(dotenv_path=".env.local")
else:
    load_dotenv()  # Default .env file

# Initialize database connection
init_db()

# fmt: off
# Use environment variable with fallback for deployment scenarios
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY", "d0f6ba4e6ca24b08a0896b004a08b2ac")
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


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Dict, int]:
    """Check the health of the application by verifying database connectivity."""
    app.logger.info("Health check requested")
    
    try:
        db_health: Dict[str, str] = check_db_health()
        app.logger.info(f"Database health check result: {db_health}")

        # Determine overall health status based on database connection and query status
        is_healthy = (
            db_health["connection"] == "healthy"
            and db_health["query"] == "healthy"
        )

        health_status = {
            "status": "healthy" if is_healthy else "unhealthy",
            "components": {
                "api": {
                    "status": "healthy",
                    "message": "API service is running"
                },
                "database": db_health,
            },
        }

        http_status = 200 if health_status["status"] == "healthy" else 503
        app.logger.info(f"Health check response: status={http_status}, body={health_status}")
        return jsonify(health_status), http_status
    except Exception as e:
        app.logger.error(f"Health check error: {str(e)}")
        error_status = {
            "status": "unhealthy",
            "components": {
                "api": {
                    "status": "unhealthy",
                    "message": f"Error during health check: {str(e)}"
                },
                "database": {
                    "connection": "unhealthy",
                    "query": "unhealthy",
                    "message": f"Exception during health check: {str(e)}"
                }
            }
        }
        return jsonify(error_status), 503


if __name__ == "__main__":
    # Always use port 5000 inside the container
    # for consistency with EXPOSE and healthchecks
    app.run(host="0.0.0.0", port=5000, debug=True)
