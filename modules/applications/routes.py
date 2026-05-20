from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.applications.service import (
    apply_to_job,
    get_applications_for_job,
    update_application_status,
    get_my_applications
)

applications_bp = Blueprint("applications", __name__, url_prefix="/applications")


# =========================================
# APPLY TO JOB (WORKER)
# POST /applications/<job_id>
# =========================================
@applications_bp.route("/<int:job_id>", methods=["POST"])
@jwt_required()
def apply(job_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()

    application, error = apply_to_job(user_id, job_id, data)

    if error:
        return jsonify({"error": error}), 400

    return jsonify({
        "message": "Application submitted successfully",
        "application": {
            "id": application.id,
            "job_id": application.job_id,
            "user_id": application.user_id,
            "message": application.message,
            "status": application.status,
            "created_at": application.created_at.isoformat()
        }
    }), 201


# =========================================
# GET APPLICATIONS FOR A JOB (CLIENT)
# GET /applications/job/<job_id>
# =========================================
@applications_bp.route("/job/<int:job_id>", methods=["GET"])
@jwt_required()
def list_applications(job_id):
    client_id = int(get_jwt_identity())

    applications, error = get_applications_for_job(job_id, client_id)

    if error:
        status_code = 404 if error == "Job not found" else 403
        return jsonify({"error": error}), status_code

    return jsonify([
        {
            "id": a.id,
            "job_id": a.job_id,
            "user_id": a.user_id,

            # SAFE RELATIONSHIP HANDLING
            "worker_name": a.user.full_name if a.user else "Unknown",
            "worker_email": a.user.email if a.user else "Unknown",

            "message": a.message,
            "status": a.status,
            "created_at": a.created_at.isoformat()
        }
        for a in applications
    ]), 200


# =========================================
# UPDATE APPLICATION STATUS (ACCEPT / REJECT)
# PUT /applications/<application_id>/status
# =========================================
@applications_bp.route("/<int:application_id>/status", methods=["PUT"])
@jwt_required()
def update_status(application_id):
    client_id = int(get_jwt_identity())
    data = request.get_json()

    status = data.get("status")

    if not status:
        return jsonify({"error": "status is required"}), 400

    application, error = update_application_status(application_id, client_id, status)

    if error:
        status_code = 404 if error == "Application not found" else 403
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Application status updated",
        "application": {
            "id": application.id,
            "status": application.status
        }
    }), 200


# =========================================
# MY APPLICATIONS (WORKER DASHBOARD)
# GET /applications/mine
# =========================================
@applications_bp.route("/mine", methods=["GET"])
@jwt_required()
def my_applications():
    user_id = int(get_jwt_identity())

    applications = get_my_applications(user_id)

    return jsonify([
        {
            "id": a.id,
            "job_id": a.job_id,
            "message": a.message,
            "status": a.status,
            "created_at": a.created_at.isoformat()
        }
        for a in applications
    ]), 200