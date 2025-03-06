from flask import jsonify, request

from ..extensions import db
from ..Models.friendshipModel import Friendship


def save_friendship():
    data = request.get_json()
    if not data or not all(
        k in data for k in ("user1_id", "user2_id", "friendship_status")
    ):
        return jsonify({"message": "Invalid input"}), 400

    new_friendship = Friendship(
        user1_id=data["user1_id"],
        user2_id=data["user2_id"],
        friendship_status=data["friendship_status"],
    )
    db.session.add(new_friendship)
    db.session.commit()
    return jsonify({"message": "Friendship saved"}), 201


def get_friendship(user1_id, user2_id):
    account = Friendship.query.filter_by(
        user1_id == user1_id, user2_id == user2_id
    ).first()
    if account is None:
        return jsonify({"message": "Friendship not found"}), 404

    return (
        jsonify(
            {
                "user1_id": account.user1_id,
                "user2_id": account.user2_id,
                "friendship_status": account.friendship_status,
                "time_created": account.time_created,
            }
        ),
        200,
    )


def update_friendship(user1_id, user2_id):
    account = Friendship.query.filter_by(
        user1_id == user1_id, user2_id == user2_id
    ).first()
    if account is None:
        return jsonify({"message": "Friendship not found"}), 404

    data = request.get_json()
    if not data or "friendship_status" not in data:
        return jsonify({"message": "Invalid input"}), 400

    if "friendship_status" in data:
        account.friendship_status = data["friendship_status"]

    db.session.commit()
    return jsonify({"message": "Friendship updated"}), 200


def delete_friendship(user1_id, user2_id):
    account = Friendship.query.filter_by(
        user1_id == user1_id, user2_id == user2_id
    ).first()
    if account is None:
        return jsonify({"message": "Friendship not found"}), 404

    db.session.delete(account)
    db.session.commit()
    return jsonify({"message": "Friendship deleted"}), 200
