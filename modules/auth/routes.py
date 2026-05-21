from . import auth_bp
from flask import request, jsonify
from models.user import User
from models.worker_profile import WorkerProfile
from flask_jwt_extended import (
    jwt_required,
    get_jwt,
    get_jwt_identity
)

from .service import (
    register_user,
    login_user,
    logout_user,
    verify_email
)


# =====================================================
# GET CURRENT USER
# =====================================================
@auth_bp.route("/me", methods=["GET"])
@jwt_required()
def get_me():

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    if not user:
        return {"error": "User not found"}, 404

    profile = None
    if user.role == "worker":
        profile = WorkerProfile.query.filter_by(user_id=user_id).first()

    return jsonify({
        "user": user.to_dict(),
        "profile": profile.to_dict() if profile else None
    }), 200


# =====================================================
# REGISTER
# =====================================================
@auth_bp.route("/register", methods=["POST"])
def register():

    data = request.get_json()
    response, status = register_user(data)
    return jsonify(response), status


# =====================================================
# LOGIN
# =====================================================
@auth_bp.route("/login", methods=["POST"])
def login():

    data = request.get_json()
    response, status = login_user(data)
    return jsonify(response), status


# =====================================================
# LOGOUT
# =====================================================
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    jwt_data = get_jwt()
    response, status = logout_user(jwt_data)
    return jsonify(response), status


# =====================================================
# EMAIL VERIFICATION
# =====================================================
@auth_bp.route("/verify/<token>", methods=["GET"])
def verify(token):

    response, status = verify_email(token)
    return jsonify(response), status