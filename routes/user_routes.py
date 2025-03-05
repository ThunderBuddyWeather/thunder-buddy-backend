from flask import Flask, jsonify, request
from main import app

from models.models import WeatherLog, User


@app.route("/register", methods=["POST"])
def register():
    """
    Register a new user.
    Expects JSON payload: { "username": "example", "password": "secret" }
    """
    data = request.get_json()
    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Username and password are required"}), 400

    username = data["username"]
    password = data["password"]

    # Check if the user already exists
    if User.query.filter_by(username=username).first():
        return jsonify({"error": "User already exists"}), 409

    # Create a new user and hash the password
    new_user = User(username=username)
    new_user.set_password(password)

    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201