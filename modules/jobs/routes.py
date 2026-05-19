from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.jobs.service import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
    delete_job
)

from models.job import Job
from models.user import User

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


# =========================
# CREATE JOB
# =========================
@jobs_bp.route("/", methods=["POST"])
@jwt_required()
def post_job():
    client_id = int(get_jwt_identity())
    data = request.get_json()

    user = User.query.get(client_id)

    if not user or user.role != "client":
        return jsonify({"error": "Only clients can post jobs"}), 403

    required = ["title", "description", "budget", "location"]

    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    job = create_job(client_id, data)

    return jsonify({
        "message": "Job created successfully",
        "job": job.to_dict()
    }), 201


# =========================
# GET ALL JOBS
# =========================
@jobs_bp.route("/", methods=["GET"])
def list_jobs():
    location = request.args.get("location")
    status = request.args.get("status")

    jobs = get_all_jobs(location=location, status=status)

    return jsonify([job.to_dict() for job in jobs]), 200


# =========================
# GET SINGLE JOB
# =========================
@jobs_bp.route("/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = get_job_by_id(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify(job.to_dict()), 200


# =========================
# UPDATE JOB
# =========================
@jobs_bp.route("/<int:job_id>", methods=["PUT"])
@jwt_required()
def edit_job(job_id):
    client_id = int(get_jwt_identity())
    data = request.get_json()

    job, error = update_job(job_id, client_id, data)

    if error:
        status_code = 404 if error == "Job not found" else 403
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Job updated",
        "job": job.to_dict()
    }), 200


# =========================
# DELETE JOB
# =========================
@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def remove_job(job_id):
    client_id = int(get_jwt_identity())

    success, error = delete_job(job_id, client_id)

    if not success:
        status_code = 404 if error == "Job not found" else 403
        return jsonify({"error": error}), status_code

    return jsonify({"message": "Job deleted successfully"}), 200