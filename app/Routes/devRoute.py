"""Development-only routes blueprint"""

import logging
from typing import Dict, List, Tuple

from flask import Blueprint, Response, current_app, jsonify

from app.Models.userAccountModel import UserAccount

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

dev_blueprint = Blueprint("dev", __name__)


@dev_blueprint.route("/health", methods=["GET"])
def dev_health_check() -> Tuple[Response, int]:
    """
    Simple health check for development endpoints
    """
    # Even the health check is only available in development mode
    if not current_app.debug:
        logger.warning("Attempted to access dev health check in non-debug mode")
        return jsonify({"message": "Not Found"}), 404
    
    return jsonify({
        "status": "ok",
        "message": "Development routes are active",
        "environment": "development"
    }), 200


@dev_blueprint.route("/users", methods=["GET"])
def list_all_users() -> Tuple[Response, int]:
    """
    List all users in the system - DEV MODE ONLY
    This endpoint is only available in development mode and should not be used in production.
    """
    # Check if we're in development mode - if not, return 404
    if not current_app.debug:
        logger.warning("Attempted to access dev-only endpoint in non-debug mode")
        return jsonify({"message": "Not Found"}), 404
    
    logger.info("Fetching all users for dev endpoint")
    
    try:
        # Query all users
        users = UserAccount.query.all()
        
        # Convert to list of dictionaries
        user_list = []
        for user in users:
            user_dict = {
                "user_id": user.user_id,
                "username": user.user_username,
                "email": user.user_email,
                "name": user.user_name,
                "location": user.user_location,
                "profile_picture": user.user_profile_picture
            }
            user_list.append(user_dict)
        
        logger.info(f"Successfully retrieved {len(user_list)} users")
        return jsonify({
            "users": user_list,
            "count": len(user_list),
            "environment": "development"
        }), 200
        
    except Exception as e:
        logger.error(f"Error retrieving users: {str(e)}")
        return jsonify({"message": "Error retrieving users"}), 500 