from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.jobs.service import (
    create_job,
    get_all_jobs,
    get_job_by_id,
    update_job,
    delete_job,
    update_job_status
)

from models.job import Job 
from flask import current_app
from werkzeug.utils import secure_filename
import os
import uuid  # IMPORTANT FIX (needed for /mine)

jobs_bp = Blueprint("jobs", __name__, url_prefix="/jobs")

ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "gif", "webp"}

def allowed_file(filename):
    return (
        "." in filename and
        filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )

# =========================
# CREATE JOB
# =========================
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


# =========================
# GET ALL JOBS
# =========================
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

            # ✅ ADD THIS
            "employer": j.client.full_name if j.client else "Unknown",
            "employer_email": j.client.email if j.client else None,

            "created_at": j.created_at.isoformat()
        }
        for j in jobs
    ]), 200


# =========================
# GET SINGLE JOB
# =========================
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


# =========================
# MY JOBS (CLIENT DASHBOARD)
# =========================
@jobs_bp.route("/mine", methods=["GET"])
@jwt_required()
def get_my_jobs():
    user_id = int(get_jwt_identity())

    jobs = Job.query.filter_by(client_id=user_id).all()

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
        }
        for j in jobs
    ]), 200


# =========================================
# UPLOAD JOB IMAGE
# POST /jobs/upload-image
# =========================================
@jobs_bp.route("/upload-image", methods=["POST"])
@jwt_required()
def upload_job_image():

    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    file = request.files["image"]

    if file.filename == "":
        return jsonify({"error": "No selected file"}), 400

    if not allowed_file(file.filename):
        return jsonify({
            "error": "Invalid file type"
        }), 400

    filename = secure_filename(file.filename)

    unique_filename = f"{uuid.uuid4()}_{filename}"

    upload_path = os.path.join(
        current_app.config["UPLOAD_FOLDER"],
        unique_filename
    )

    file.save(upload_path)

    image_url = (
        f"{current_app.config['BACKEND_URL']}"
        f"/static/uploads/{unique_filename}"
    )

    return jsonify({
        "message": "Image uploaded successfully",
        "image_url": image_url
    }), 201


# =========================
# UPDATE JOB STATUS
# =========================
@jobs_bp.route("/<int:job_id>/status", methods=["PUT"])
@jwt_required()
def update_job_status_endpoint(job_id):
    client_id = int(get_jwt_identity())
    data = request.get_json()

    status = data.get("status")
    if not status:
        return jsonify({"error": "status is required"}), 400

    job, error = update_job_status(job_id, client_id, status)

    if error:
        status_code = 404 if error == "Job not found" else 403
        return jsonify({"error": error}), status_code

    return jsonify({
        "message": "Job status updated",
        "job": {
            "id": job.id,
            "status": job.status
        }
    }), 200