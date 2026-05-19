from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.jobs.service import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
    delete_job
)

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")


@jobs_bp.route("/", methods=["POST"])
@jwt_required()
def post_job():
    client_id = int(get_jwt_identity())
    data = request.get_json()

    required = ["title", "description", "budget", "location"]

    for field in required:
        if not data.get(field):
            return jsonify({"error": f"{field} is required"}), 400

    job = create_job(client_id, data)

    return jsonify({
        "message": "Job created successfully",
        "job": {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "category": job.category,
            "budget": job.budget,
            "location": job.location,
            "status": job.status,
            "urgency": job.urgency,
            "duration": job.duration,
            "contact_method": job.contact_method,
            "image_url": job.image_url,
            "client_id": job.client_id,
            "created_at": job.created_at.isoformat()
        }
    }), 201


@jobs_bp.route("/", methods=["GET"])
def list_jobs():
    location = request.args.get("location")
    status = request.args.get("status")

    jobs = get_all_jobs(location=location, status=status)

    return jsonify([
        {
            "id": j.id,
            "title": j.title,
            "description": j.description,
            "category": j.category,
            "budget": j.budget,
            "location": j.location,
            "status": j.status,
            "urgency": j.urgency,
            "duration": j.duration,
            "contact_method": j.contact_method,
            "image_url": j.image_url,
            "client_id": j.client_id,
            "created_at": j.created_at.isoformat()
        } for j in jobs
    ]), 200


@jobs_bp.route("/<int:job_id>", methods=["GET"])
def get_job(job_id):
    job = get_job_by_id(job_id)

    if not job:
        return jsonify({"error": "Job not found"}), 404

    return jsonify({
        "id": job.id,
        "title": job.title,
        "description": job.description,
        "category": job.category,
        "budget": job.budget,
        "location": job.location,
        "status": job.status,
        "urgency": job.urgency,
        "duration": job.duration,
        "contact_method": job.contact_method,
        "image_url": job.image_url,
        "client_id": job.client_id,
        "created_at": job.created_at.isoformat()
    }), 200


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
        "job": {
            "id": job.id,
            "title": job.title,
            "description": job.description,
            "category": job.category,
            "budget": job.budget,
            "location": job.location,
            "status": job.status,
            "urgency": job.urgency,
            "duration": job.duration,
            "contact_method": job.contact_method,
            "image_url": job.image_url
        }
    }), 200


@jobs_bp.route("/<int:job_id>", methods=["DELETE"])
@jwt_required()
def remove_job(job_id):
    client_id = int(get_jwt_identity())

    success, error = delete_job(job_id, client_id)

    if not success:
        status_code = 404 if error == "Job not found" else 403
        return jsonify({"error": error}), status_code

    return jsonify({"message": "Job deleted successfully"}), 200