from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.users.service import (
    get_user_profile,
    update_user_profile,
    delete_user
)

users_bp = Blueprint("users", __name__, url_prefix="/users")


@users_bp.route("/<int:user_id>", methods=["GET"])
def profile(user_id):
    user, error = get_user_profile(user_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(user), 200


@users_bp.route("/me", methods=["GET"])
@jwt_required()
def me():
    user_id = int(get_jwt_identity())
    user, error = get_user_profile(user_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify(user), 200


@users_bp.route("/me", methods=["PUT"])
@jwt_required()
def update_me():
    user_id = int(get_jwt_identity())
    data = request.get_json()
    user, error = update_user_profile(user_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "full_name": user.full_name,
            "phone": user.phone,
            "location": user.location,
            "profile_image": user.profile_image
        }
    }), 200


@users_bp.route("/me", methods=["DELETE"])
@jwt_required()
def delete_me():
    user_id = int(get_jwt_identity())
    success, error = delete_user(user_id)
    if not success:
        return jsonify({"error": error}), 404
    return jsonify({"message": "Account deleted successfully"}), 200