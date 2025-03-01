"""
Thunder Buddy API service built with Flask
Provides user account management and friendship features
"""

from typing import Dict, Tuple

from dotenv import load_dotenv
from flask import jsonify

from app import create_app
from scripts.db import test_connection as check_db_health

# Load environment variables
load_dotenv()

# Create the application instance
app = create_app("development")


@app.route("/", methods=["GET"])
def hello_world():
    """Root endpoint that returns a greeting."""
    return jsonify({"Message": "Hello World"}), 200


@app.route("/health", methods=["GET"])
def health_check() -> Tuple[Dict, int]:
    """Check the health of the application by verifying database connectivity."""
    db_health: Dict[str, str] = check_db_health()

    # Determine overall health status based on database connection and query status
    is_healthy = (
        db_health["connection"] == "healthy" and db_health["query"] == "healthy"
    )

    health_status = {
        "status": "healthy" if is_healthy else "unhealthy",
        "components": {
            "api": {"status": "healthy", "message": "API service is running"},
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
        use_reloader=True,  # Enables auto-reload
    )
