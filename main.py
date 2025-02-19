from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests
import os


app = Flask(__name__)

load_dotenv()

WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY", "d0f6ba4e6ca24b08a0896b004a08b2ac")


@app.route('/', methods=['GET'])
def hello_world():
    return jsonify({"Message": "Hello World"}), 200

@app.route('/weather', methods=['GET'])
def get_local_weather():
    zip_code = request.args.get('zip', '30152') # Default to 30152 if not provided
    country = request.args.get('country', 'US')  # Default to US if not provided
    
    if not zip_code:
        return jsonify({"error": "ZIP code is required"}), 400

    weatherbit_url = f"https://api.weatherbit.io/v2.0/current"
    params = {
        "postal_code": zip_code,
        "country": country,
        "units": "I",  # "I" for Fahrenheit, "M" for Celsius (default)
        "key": WEATHERBIT_API_KEY
    }

    response = requests.get(weatherbit_url, params=params)

    if response.status_code != 200:
        return jsonify({"error": "Failed to fetch weather data"}), response.status_code

    return jsonify(response.json())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
