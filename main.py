"""
Weather API service built with Flask
Provides current weather data through REST endpoints
"""

import logging
import os

import requests  # noqa: E402
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_from_directory

# Import our database module
from scripts.db import init_db
from scripts.db import test_connection as check_db_health

# Import routes
from routes.user_routes import user_routes
from routes.test_routes import test_routes
from routes.weather_routes import weather_routes

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

# Add a route to serve swagger.yaml with the correct MIME type
@app.route('/static/swagger.yaml')
def serve_swagger():
    """Serve the swagger.yaml file with the correct MIME type"""
    return send_from_directory('static', 'swagger.yaml', mimetype='application/yaml')

load_dotenv()

# Initialize database connection
init_db()

# fmt: off
WEATHERBIT_API_KEY = os.getenv("WEATHERBIT_API_KEY",
                               "d0f6ba4e6ca24b08a0896b004a08b2ac")  # noqa: E501
timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))  # Default as string "10"
# fmt: on

# Configure logging
logging.basicConfig(level=logging.ERROR)



# app.register_blueprint(user_routes)
app.register_blueprint(test_routes)
app.register_blueprint(weather_routes)








if __name__ == "__main__":
    # Always use port 5000 inside the container
    # for consistency with EXPOSE and healthchecks
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,  # Enables debug mode
        use_reloader=True  # Enables auto-reload
    )
