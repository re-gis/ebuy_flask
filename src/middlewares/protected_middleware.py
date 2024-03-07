import jwt
from flask import request, jsonify
from functools import wraps
import os


def token_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = None

        # Check if 'Authorization' header is present in the request
        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split()[1]  # Get token from header

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            # Decode the token
            data = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=["HS256"])
            user = {
                "user_id": data["user_id"],
                "username": data["username"],
                "email": data["email"],
                "role": data["role"],
            }

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token is expired"}), 401
        except jwt.InvalidTokenError as e:
            print(e)
            return jsonify({"error": "Invalid token"}), 401

        return f(user, *args, **kwargs)

    return decorated_function
