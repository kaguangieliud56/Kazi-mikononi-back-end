from . import auth_bp
from flask import request, jsonify

from .service import register_user, login_user


@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    response, status = register_user(data)

    return jsonify(response), status


@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    response, status = login_user(data)

    return jsonify(response), status