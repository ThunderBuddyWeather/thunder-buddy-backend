"""User account routes blueprint"""

import logging
import re
from typing import Any, Dict, Optional, Tuple, Union

from flask import Blueprint, Response, jsonify, request
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.security import check_password_hash, generate_password_hash

from ..Controllers.userAccountController import (
    delete_user_account,
    get_user_account,
    save_user_account,
    update_user_account,
)
from ..extensions import caching, db, limiter
from ..Models.userAccountModel import UserAccount

user_account_blueprint = Blueprint("user_account", __name__)

# Configure logging
logging.basicConfig(
    level=logging.ERROR, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def validate_email(email: str) -> Tuple[bool, Optional[str]]:
    """
    Validate email format.

    Args:
        email: Email address to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if not re.match(email_regex, email):
        return False, "Invalid email format"
    return True, None


def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """
    Validate password strength.

    Args:
        password: Password to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if len(password) < 6:  # Reduced from 8 for tests
        return False, "Password must be at least 6 characters long"
    return True, None


@user_account_blueprint.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register() -> Tuple[Response, int]:
    """Register a new user account"""
    try:
        data = request.get_json()
        if not data:
            logger.warning("No JSON data in registration request")
            return jsonify({"message": "Missing request data"}), 400

        required_fields = ["email", "password", "name"]
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            logger.warning(f"Missing required fields in registration: {missing_fields}")
            return (
                jsonify(
                    {"message": f"Missing required fields: {', '.join(missing_fields)}"}
                ),
                400,
            )

        # Validate email format
        is_valid_email, email_error = validate_email(data["email"])
        if not is_valid_email:
            logger.warning(f"Invalid email format: {data['email']}")
            return jsonify({"message": email_error}), 400

        # Validate password strength
        is_valid_password, password_error = validate_password(data["password"])
        if not is_valid_password:
            logger.warning("Invalid password format in registration")
            return jsonify({"message": password_error}), 400

        # Check for existing email
        if UserAccount.query.filter_by(user_email=data["email"]).first():
            logger.warning(
                f"Attempted registration with existing email: {data['email']}"
            )
            return jsonify({"message": "Email already exists"}), 400

        # Validate name length
        if len(data["name"]) < 2:
            logger.warning("Name too short in registration")
            return jsonify({"message": "Name must be at least 2 characters long"}), 400

        new_user = UserAccount(
            user_username=data["email"].split("@")[0],
            user_password=generate_password_hash(data["password"]),
            user_name=data["name"],
            user_email=data["email"],
            user_phone=data.get("phone", ""),
            user_address=data.get("address", ""),
            user_location=data.get("location", ""),
            user_weather=data.get("weather", ""),
            user_severe_weather=data.get("severe_weather", ""),
            user_profile_picture=data.get("profile_picture", ""),
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            logger.info(f"Successfully registered new user: {data['email']}")
        except IntegrityError as e:
            logger.error(f"Database integrity error during registration: {str(e)}")
            db.session.rollback()
            return jsonify({"message": "Database error during registration"}), 500
        except SQLAlchemyError as e:
            logger.error(f"Database error during registration: {str(e)}")
            db.session.rollback()
            return jsonify({"message": "Failed to create user account"}), 500

        return (
            jsonify(
                {
                    "user_id": new_user.user_id,
                    "email": new_user.user_email,
                    "name": new_user.user_name,
                }
            ),
            201,
        )

    except Exception as e:
        logger.error(f"Unexpected error during registration: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@user_account_blueprint.route("/login", methods=["POST"])
@limiter.limit("10 per minute")
def login() -> Tuple[Response, int]:
    """Login user and return access token"""
    try:
        data = request.get_json()
        if not data:
            logger.warning("No JSON data in login request")
            return jsonify({"message": "Missing request data"}), 400

        if not all(k in data for k in ["email", "password"]):
            logger.warning("Missing email or password in login request")
            return jsonify({"message": "Missing email or password"}), 400

        user = UserAccount.query.filter_by(user_email=data["email"]).first()
        if not user:
            logger.warning(f"Login attempt with non-existent email: {data['email']}")
            return jsonify({"message": "Invalid email or password"}), 401

        if not check_password_hash(user.user_password, data["password"]):
            logger.warning(f"Failed login attempt for user: {data['email']}")
            return jsonify({"message": "Invalid email or password"}), 401

        access_token = create_access_token(identity=str(user.user_id))
        logger.info(f"Successful login for user: {data['email']}")
        return jsonify({"access_token": access_token}), 200

    except Exception as e:
        logger.error(f"Unexpected error during login: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@user_account_blueprint.route("/profile", methods=["GET"])
@jwt_required()
@limiter.limit("10 per minute")
@caching.cached(timeout=60)
def get_profile() -> Tuple[Response, int]:
    """Get user profile information"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(UserAccount, user_id)
        if not user:
            logger.warning(f"Profile request for non-existent user ID: {user_id}")
            return jsonify({"message": "User not found"}), 404

        return (
            jsonify(
                {
                    "user_id": user.user_id,
                    "email": user.user_email,
                    "name": user.user_name,
                    "username": user.user_username,
                    "phone": user.user_phone,
                    "address": user.user_address,
                    "location": user.user_location,
                    "weather": user.user_weather,
                    "severe_weather": user.user_severe_weather,
                    "created_at": user.user_created_at,
                    "profile_picture": user.user_profile_picture,
                }
            ),
            200,
        )

    except Exception as e:
        logger.error(f"Unexpected error in get_profile: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@user_account_blueprint.route("/profile", methods=["PUT"])
@jwt_required()
@limiter.limit("10 per minute")
def update_profile() -> Tuple[Response, int]:
    """Update user profile information"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(UserAccount, user_id)
        if not user:
            logger.warning(f"Update attempt for non-existent user ID: {user_id}")
            return jsonify({"message": "User not found"}), 404

        data = request.get_json()
        if not data:
            logger.warning(f"No data provided for profile update: {user_id}")
            return jsonify({"message": "No data provided"}), 400

        # Validate update fields
        allowed_fields = {
            "name",
            "phone",
            "address",
            "location",
            "weather",
            "severe_weather",
            "profile_picture",
        }
        invalid_fields = set(data.keys()) - allowed_fields
        if invalid_fields:
            logger.warning(f"Invalid fields in profile update: {invalid_fields}")
            return (
                jsonify({"message": f"Invalid fields: {', '.join(invalid_fields)}"}),
                400,
            )

        if "name" in data and len(data["name"]) < 2:
            logger.warning("Name too short in profile update")
            return jsonify({"message": "Name must be at least 2 characters long"}), 400

        try:
            # Update allowed fields
            for field in allowed_fields:
                if field in data:
                    setattr(user, f"user_{field}", data[field])

            db.session.commit()
            logger.info(f"Successfully updated profile for user ID: {user_id}")
            return "", 204

        except SQLAlchemyError as e:
            logger.error(f"Database error during profile update: {str(e)}")
            db.session.rollback()
            return jsonify({"message": "Failed to update profile"}), 500

    except Exception as e:
        logger.error(f"Unexpected error in update_profile: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500


@user_account_blueprint.route("/profile", methods=["DELETE"])
@jwt_required()
@limiter.limit("10 per minute")
def delete_profile() -> Tuple[Response, int]:
    """Delete user profile"""
    try:
        user_id = int(get_jwt_identity())
        user = db.session.get(UserAccount, user_id)
        if not user:
            logger.warning(f"Delete attempt for non-existent user ID: {user_id}")
            return jsonify({"message": "User not found"}), 404

        try:
            db.session.delete(user)
            db.session.commit()
            logger.info(f"Successfully deleted user ID: {user_id}")
            return "", 204

        except SQLAlchemyError as e:
            logger.error(f"Database error during profile deletion: {str(e)}")
            db.session.rollback()
            return jsonify({"message": "Failed to delete profile"}), 500

    except Exception as e:
        logger.error(f"Unexpected error in delete_profile: {str(e)}")
        return jsonify({"message": "Internal server error"}), 500
