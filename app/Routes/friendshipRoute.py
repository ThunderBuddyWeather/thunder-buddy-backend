"""Friendship routes blueprint"""

import logging
from typing import Any, Dict, Optional, Tuple

from flask import Blueprint, jsonify, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy.exc import SQLAlchemyError

from ..extensions import caching, db, limiter
from ..Models.friendshipModel import Friendship
from ..Models.userAccountModel import UserAccount

friendship_blueprint = Blueprint("friendship", __name__, url_prefix="/api/friends")

# Configure logging
logging.basicConfig(
    level=logging.WARNING, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def get_friendship(user_id: int, friend_id: int) -> Optional[Friendship]:
    """Get friendship between two users if it exists"""
    return Friendship.query.filter(
        ((Friendship.user1_id == user_id) & (Friendship.user2_id == friend_id))
        | ((Friendship.user1_id == friend_id) & (Friendship.user2_id == user_id))
    ).first()


@friendship_blueprint.route("/request/<int:friend_id>", methods=["POST"])
@jwt_required()
@limiter.limit("5 per minute")
def send_friend_request(friend_id: int) -> Tuple[Dict[str, Any], int]:
    """Send a friend request to another user"""
    try:
        user_id = int(get_jwt_identity())
        if user_id == friend_id:
            logger.warning(f"User {user_id} attempted to friend themselves")
            return {"message": "Cannot send friend request to yourself"}, 400

        # Check if friend exists
        friend = UserAccount.query.get(friend_id)
        if not friend:
            logger.warning(f"Friend with id {friend_id} not found")
            return {"message": "User not found"}, 404

        # Check if friendship already exists
        existing_friendship = get_friendship(user_id, friend_id)
        if existing_friendship:
            if existing_friendship.friendship_status == "pending":
                return {"error": "Friendship already exists"}, 400
            elif existing_friendship.friendship_status == "accepted":
                return {"error": "Friendship already exists"}, 400
            elif existing_friendship.friendship_status == "rejected":
                return {"error": "Friendship already exists"}, 400

        # Create new friendship
        new_friendship = Friendship(
            user1_id=user_id, user2_id=friend_id, friendship_status="pending"
        )
        db.session.add(new_friendship)
        db.session.commit()

        return {"message": "Friend request sent", "status": "pending"}, 201

    except SQLAlchemyError as e:
        logger.error(f"Database error in send_friend_request: {str(e)}")
        db.session.rollback()
        return {"error": "Database error"}, 500
    except Exception as e:
        logger.error(f"Unexpected error in send_friend_request: {str(e)}")
        return {"error": "An unexpected error occurred"}, 500


@friendship_blueprint.route("/accept/<int:user_id>", methods=["PUT"])
@jwt_required()
@limiter.limit("5 per minute")
def accept_friend_request(user_id: int) -> Tuple[Dict[str, Any], int]:
    """Accept a friend request"""
    try:
        friend_id = int(get_jwt_identity())

        # Check if friendship exists
        friendship = get_friendship(user_id, friend_id)
        if not friendship:
            logger.warning(f"Friendship between {user_id} and {friend_id} not found")
            return {"message": "Friendship not found"}, 404

        if friendship.friendship_status != "pending":
            logger.warning(f"Invalid friendship status: {friendship.friendship_status}")
            return {"message": "Invalid friendship status"}, 400

        # Update friendship status
        friendship.friendship_status = "accepted"
        db.session.commit()

        return {"message": "Friend request accepted"}, 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in accept_friend_request: {str(e)}")
        db.session.rollback()
        return {"error": "Database error"}, 500
    except Exception as e:
        logger.error(f"Unexpected error in accept_friend_request: {str(e)}")
        return {"error": "An unexpected error occurred"}, 500


@friendship_blueprint.route("/reject/<int:friend_id>", methods=["PUT"])
@jwt_required()
@limiter.limit("5 per minute") 
def reject_friend_request(friend_id: int) -> Tuple[Dict[str, Any], int]:
    """Reject a friend request"""
    try:
        current_user_id = int(get_jwt_identity())

        friendship = get_friendship(current_user_id, friend_id)
        if not friendship:
            logger.warning(
                f"Friendship not found between {current_user_id} and {friend_id}"
            )
            return {"message": "Friendship not found"}, 404

        if friendship.friendship_status != "pending":
            logger.warning(
                f"Cannot reject friendship that is not pending (status: {friendship.friendship_status})"
            )
            return {
                "message": f"Cannot reject friendship with status: {friendship.friendship_status}"
            }, 409

        friendship.friendship_status = "rejected"
        db.session.commit()

        return {}, 204

    except SQLAlchemyError as e:
        logger.error(f"Database error in reject_friend_request: {str(e)}")
        db.session.rollback()
        return {"message": "Failed to reject friend request"}, 500
    except Exception as e:
        logger.error(f"Unexpected error in reject_friend_request: {str(e)}")
        return {"message": "An unexpected error occurred"}, 500


@friendship_blueprint.route("", methods=["GET"])
@jwt_required()
@limiter.limit("10 per minute")
def get_friends_list() -> Tuple[Dict[str, Any], int]:
    """Get list of friends"""
    try:
        user_id = int(get_jwt_identity())

        # Get all accepted friendships
        friendships = Friendship.query.filter(
            ((Friendship.user1_id == user_id) | (Friendship.user2_id == user_id))
            & (Friendship.friendship_status == "accepted")
        ).all()

        friends_list = []
        for friendship in friendships:
            friend_id = (
                friendship.user2_id
                if friendship.user1_id == user_id
                else friendship.user1_id
            )
            friend = UserAccount.query.get(friend_id)
            if friend:
                friends_list.append(
                    {
                        "user_id": friend.user_id,
                        "name": friend.user_name,
                        "email": friend.user_email,
                    }
                )

        return {"friends": friends_list}, 200

    except SQLAlchemyError as e:
        logger.error(f"Database error in get_friends_list: {str(e)}")
        return {"error": "Database error"}, 500
    except Exception as e:
        logger.error(f"Unexpected error in get_friends_list: {str(e)}")
        return {"error": "An unexpected error occurred"}, 500


@friendship_blueprint.route("/<int:friend_id>", methods=["DELETE"])
@jwt_required()
@limiter.limit("5 per minute")
def unfriend(friend_id: int) -> Tuple[Dict[str, Any], int]:
    """Remove a friend"""
    try:
        user_id = int(get_jwt_identity())

        # Check if friendship exists
        friendship = get_friendship(user_id, friend_id)
        if not friendship:
            logger.warning(f"Friendship between {user_id} and {friend_id} not found")
            return {"message": "Friendship not found"}, 404

        # Check if friendship is accepted
        if friendship.friendship_status != "accepted":
            logger.warning(
                f"Cannot unfriend with status: {friendship.friendship_status}"
            )
            return {"message": "Can only unfriend accepted friendships"}, 409

        # Delete friendship
        db.session.delete(friendship)
        db.session.commit()

        return {}, 204

    except SQLAlchemyError as e:
        logger.error(f"Database error in unfriend: {str(e)}")
        db.session.rollback()
        return {"error": "Database error"}, 500
    except Exception as e:
        logger.error(f"Unexpected error in unfriend: {str(e)}")
        return {"error": "An unexpected error occurred"}, 500
