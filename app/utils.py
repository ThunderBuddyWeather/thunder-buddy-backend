import os
from datetime import datetime, timedelta, timezone
from functools import wraps
from typing import Any, Callable, TypeVar, cast

import jwt
from dotenv import load_dotenv
from flask import current_app, jsonify, request

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")


def get_remote_address() -> str:
    """Get the remote address of the request"""
    return request.remote_addr or "127.0.0.1"


def encode_token(user_id: int) -> str:
    """Generate JWT token for user"""
    payload = {
        "exp": datetime.now(timezone.utc) + timedelta(days=1),
        "iat": datetime.now(timezone.utc),
        "sub": str(user_id),
    }
    token = jwt.encode(payload, current_app.config["SECRET_KEY"], algorithm="HS256")
    return token


def token_required(f: Callable) -> Callable:
    @wraps(f)
    def decorated(*args: Any, **kwargs: Any) -> Any:
        token = None
        if "Authorization" in request.headers:
            auth_header = request.headers["Authorization"]
            try:
                token = auth_header.split(" ")[1]
            except IndexError:
                return jsonify({"message": "Token is missing"}), 401

        if not token:
            return jsonify({"message": "Token is missing"}), 401

        try:
            payload = jwt.decode(
                token, current_app.config["SECRET_KEY"], algorithms=["HS256"]
            )
            # 'current_user_id' is assigned but not used, just decode the token to validate it
            _ = int(payload["sub"])
        except jwt.ExpiredSignatureError:
            return jsonify({"message": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"message": "Token is invalid"}), 401
        except Exception:
            return jsonify({"message": "Token is invalid"}), 401

        return f(*args, **kwargs)

    return decorated
