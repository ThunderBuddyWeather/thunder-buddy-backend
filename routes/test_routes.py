from flask import Blueprint, jsonify, request

from datetime import datetime
from typing import Dict, Tuple
from scripts.db import test_connection as check_db_health


test_routes = Blueprint('test_routes', __name__)


@test_routes.route("/", methods=["GET"])
def hello_world():
    """Return a simple greeting message"""
    return jsonify({"Message": "Hello World"}), 200


@test_routes.route("/test", methods=["GET"])
def test():
    """Test endpoint that returns a message with timestamp"""
    return jsonify({
        "message": "this works",
        "timestamp": datetime.now().isoformat(),
        "auto_reload": "Auto-reload is now working in Docker with direct source code mounting!!!!!"
    }), 200



@test_routes.route("/health", methods=["GET"])
def health_check() -> Tuple[Dict, int]:
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
