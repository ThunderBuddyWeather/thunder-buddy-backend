"""
Weather API service built with Flask
Provides current weather data through REST endpoints
"""

import logging
import os

import psycopg2
import requests  # noqa: E402
from dotenv import load_dotenv
from flask import Flask, jsonify, request

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


@app.route("/health", methods=["GET"])
def health_check():
    """Check the health of the application by verifying database connectivity."""
    try:
        if test_connection():
            return jsonify({'status': 'healthy', 'db': 'connected'}), 200
        return jsonify({'status': 'unhealthy', 'db': 'disconnected'}), 500
    except (psycopg2.Error, KeyError) as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)
