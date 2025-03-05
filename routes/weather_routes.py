from flask import Blueprint, jsonify, request

from datetime import datetime
from typing import Dict, Tuple
from scripts.db import test_connection as check_db_health

import requests

from main import WEATHERBIT_API_KEY, timeout


weather_routes = Blueprint('weather_routes', __name__)


@weather_routes.route("/weather", methods=["GET"])
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