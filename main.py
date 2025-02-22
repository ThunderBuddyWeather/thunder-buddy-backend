"""
Weather API service built with Flask
Provides current weather data through REST endpoints
"""

import os
import json

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests  # noqa: E402  # Import not at top of file


app = Flask(__name__)

load_dotenv()

# fmt: off
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY",
                               "d0f6ba4e6ca24b08a0896b004a08b2ac")  # noqa: E501
timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))  # Default as string "10"
# fmt: on


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

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch weather data"}), response.status_code

        return jsonify(response.json())
    except TimeoutError:
        return jsonify({"error": "Request timed out"}), 500
    except requests.RequestException:
        return jsonify({"error": "API request failed"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Invalid response format"}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
