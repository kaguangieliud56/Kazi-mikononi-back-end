# modules/workers/routes.py

from flask import Blueprint, request, jsonify

from flask_jwt_extended import (
    jwt_required,
    get_jwt_identity
)

from .service import (
    create_or_update_profile,
    get_profile,
    add_skill_to_worker,
    remove_skill_from_worker,
    get_worker_skills,
    set_availability,
    get_availability,
    get_all_workers
)

worker_bp = Blueprint(
    "workers",
    __name__,
    url_prefix="/workers"
)


# -----------------------------------------
# CREATE / UPDATE WORKER PROFILE
# -----------------------------------------
@worker_bp.route("/profile", methods=["POST"])
@jwt_required()
def save_profile():

    user_id = get_jwt_identity()

    data = request.get_json()

    response, status = create_or_update_profile(
        user_id,
        data
    )

    return jsonify(response), status


# -----------------------------------------
# GET CURRENT WORKER PROFILE
# -----------------------------------------
@worker_bp.route("/profile", methods=["GET"])
@jwt_required()
def fetch_profile():

    user_id = get_jwt_identity()

    response, status = get_profile(user_id)

    return jsonify(response), status


# -----------------------------------------
# ADD SKILL TO WORKER
# -----------------------------------------
@worker_bp.route("/skills", methods=["POST"])
@jwt_required()
def add_skill():

    user_id = get_jwt_identity()

    data = request.get_json()

    response, status = add_skill_to_worker(
        user_id,
        data["skill"]
    )

    return jsonify(response), status


# -----------------------------------------
# REMOVE SKILL FROM WORKER
# -----------------------------------------
@worker_bp.route("/skills", methods=["DELETE"])
@jwt_required()
def remove_skill():

    user_id = get_jwt_identity()

    data = request.get_json()

    response, status = remove_skill_from_worker(
        user_id,
        data["skill"]
    )

    return jsonify(response), status


# -----------------------------------------
# GET WORKER SKILLS
# -----------------------------------------
@worker_bp.route("/skills", methods=["GET"])
@jwt_required()
def get_skills():

    user_id = get_jwt_identity()

    response, status = get_worker_skills(user_id)

    return jsonify(response), status


# -----------------------------------------
# SET AVAILABILITY
# -----------------------------------------
@worker_bp.route("/availability", methods=["POST"])
@jwt_required()
def availability():

    user_id = get_jwt_identity()

    data = request.get_json()

    response, status = set_availability(
        user_id,
        data
    )

    return jsonify(response), status


# -----------------------------------------
# GET AVAILABILITY
# -----------------------------------------
@worker_bp.route("/availability", methods=["GET"])
@jwt_required()
def get_avail():

    user_id = get_jwt_identity()

    response, status = get_availability(user_id)

    return jsonify(response), status


# -----------------------------------------
# GET ALL WORKERS
# -----------------------------------------
@worker_bp.route("/", methods=["GET"])
def get_all_workers_route():

    response, status = get_all_workers()

    return jsonify(response), status