from typing import Any, Dict, Tuple

from flask import Response, jsonify, request
from sqlalchemy.exc import SQLAlchemyError
from werkzeug.security import generate_password_hash

from app.extensions import db
from app.Models.userAccountModel import UserAccount


def save_user_account() -> Tuple[Response, int]:
    try:
        data = request.get_json()
        required_fields = [
            "user_username",
            "user_password",
            "user_name",
            "user_email",
            "user_phone",
            "user_address",
            "user_location",
            "user_weather",
            "user_profile_picture",
        ]

        if not data or not all(field in data for field in required_fields):
            return jsonify({"message": "Invalid input"}), 400

        new_account = UserAccount(
            user_username=data["user_username"],
            user_password=generate_password_hash(data["user_password"]),
            user_name=data["user_name"],
            user_email=data["user_email"],
            user_phone=data["user_phone"],
            user_address=data["user_address"],
            user_location=data["user_location"],
            user_weather=data["user_weather"],
            user_profile_picture=data["user_profile_picture"],
        )

        db.session.add(new_account)
        db.session.commit()
        return jsonify({"message": "User account saved"}), 201
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500


def get_user_account(user_id: int) -> Tuple[Response, int]:
    try:
        account = UserAccount.query.filter_by(user_id=user_id).first()
        if account is None:
            return jsonify({"message": "User account not found"}), 404

        return (
            jsonify(
                {
                    "user_id": account.user_id,
                    "user_username": account.user_username,
                    "user_name": account.user_name,
                    "user_email": account.user_email,
                    "user_phone": account.user_phone,
                    "user_address": account.user_address,
                    "user_location": account.user_location,
                    "user_weather": account.user_weather,
                    "user_profile_picture": account.user_profile_picture,
                    "user_time_created": account.user_time_created.strftime(
                        "%Y-%m-%d %H:%M:%S"
                    ),
                }
            ),
            200,
        )
    except SQLAlchemyError as e:
        return jsonify({"message": f"Database error: {str(e)}"}), 500


def _update_account_fields(account: UserAccount, data: Dict[str, Any]) -> UserAccount:
    """Helper function to update user account fields from data dictionary."""
    field_mapping = {
        "user_username": "user_username",
        "user_name": "user_name",
        "user_email": "user_email",
        "user_phone": "user_phone",
        "user_address": "user_address",
        "user_location": "user_location",
        "user_weather": "user_weather",
        "user_profile_picture": "user_profile_picture",
    }

    # Handle each field
    for key, attr in field_mapping.items():
        if key in data:
            setattr(account, attr, data[key])

    # Handle password separately due to hashing
    if "user_password" in data:
        account.user_password = generate_password_hash(data["user_password"])

    return account


def update_user_account(user_id: int) -> Tuple[Response, int]:
    try:
        # Fetch the account
        account = UserAccount.query.filter_by(user_id=user_id).first()
        if account is None:
            return jsonify({"message": "User account not found"}), 404

        # Get and validate input data
        data = request.get_json()
        if not data:
            return jsonify({"message": "Invalid input"}), 400

        # Update the account fields
        _update_account_fields(account, data)

        # Save changes
        db.session.commit()
        return jsonify({"message": "User account updated"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500


def delete_user_account(user_id: int) -> Tuple[Response, int]:
    try:
        account = UserAccount.query.filter_by(user_id=user_id).first()
        if account is None:
            return jsonify({"message": "User account not found"}), 404

        db.session.delete(account)
        db.session.commit()
        return jsonify({"message": "User account deleted"}), 200
    except SQLAlchemyError as e:
        db.session.rollback()
        return jsonify({"message": f"Database error: {str(e)}"}), 500
