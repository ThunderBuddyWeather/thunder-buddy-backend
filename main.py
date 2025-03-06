"""
Weather API service built with Flask
Provides current weather data through REST endpoints
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, Tuple

import requests  # noqa: E402
from dotenv import load_dotenv
from flask import Flask, Response, jsonify, request, send_from_directory

# Import our database module
from scripts.db import init_db
from scripts.db import test_connection as check_db_health

try:
    from flask_swagger_ui import get_swaggerui_blueprint  # type: ignore
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
def serve_swagger() -> Any:
    """Serve the swagger.yaml file with the correct MIME type"""
    return send_from_directory('static', 'swagger.yaml', mimetype='application/yaml')


load_dotenv()

# Initialize database connection
init_db()

# fmt: off
timeout = int(os.getenv("REQUEST_TIMEOUT", "10"))  # Default as string "10"
# fmt: on

# Configure logging
logging.basicConfig(level=logging.ERROR)


@app.route("/", methods=["GET"])
def hello_world() -> Tuple[Response, int]:
    """Return a simple greeting message"""
    return jsonify({"Message": "Hello World"}), 200


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Response, int]:
    """Check the health of the application by verifying database connectivity."""
    db_health: Dict[str, str] = check_db_health()

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
    return jsonify(health_status), http_status


if __name__ == "__main__":
    # Always use port 5000 inside the container
    # for consistency with EXPOSE and healthchecks
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True,  # Enables debug mode
        use_reloader=True  # Enables auto-reload
    )
