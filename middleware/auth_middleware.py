from functools import wraps
from flask import jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from models.user import User

def role_required(*roles):
    def decorator(f):
        @wraps(f)
        @jwt_required()
        def decorated_function(*args, **kwargs):
            user_id = int(get_jwt_identity())
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            if user.role not in roles:
                return jsonify({"error": "Access denied. Insufficient permissions"}), 403
            return f(*args, **kwargs)
        return decorated_function
    return decorator