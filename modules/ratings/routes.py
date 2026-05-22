from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.ratings.service import (
    submit_rating,
    submit_client_rating,
    get_worker_ratings,
    get_client_ratings
)

ratings_bp = Blueprint("ratings", __name__, url_prefix="/ratings")


@ratings_bp.route("/workers/<int:worker_id>", methods=["POST"])
@jwt_required()
def rate_worker(worker_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    rating, error = submit_rating(user_id, worker_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({
        "message": "Rating submitted successfully",
        "rating": {
            "id": rating.id,
            "worker_id": rating.worker_id,
            "job_id": rating.job_id,
            "score": rating.score,
            "comment": rating.comment,
            "created_at": rating.created_at.isoformat()
        }
    }), 201


@ratings_bp.route("/workers/<int:worker_id>", methods=["GET"])
def get_ratings(worker_id):
    ratings, average, error = get_worker_ratings(worker_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({
        "worker_id": worker_id,
        "average_score": average,
        "total_ratings": len(ratings),
        "ratings": [
            {
                "id": r.id,
                "score": r.score,
                "comment": r.comment,
                "user_id": r.user_id,
                "job_id": r.job_id,
                "created_at": r.created_at.isoformat()
            } for r in ratings
        ]
    }), 200


@ratings_bp.route("/clients/<int:client_id>", methods=["POST"])
@jwt_required()
def rate_client(client_id):
    user_id = int(get_jwt_identity())
    data = request.get_json()
    rating, error = submit_client_rating(user_id, client_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({
        "message": "Rating submitted successfully",
        "rating": {
            "id": rating.id,
            "client_id": rating.worker_id,
            "job_id": rating.job_id,
            "score": rating.score,
            "comment": rating.comment,
            "created_at": rating.created_at.isoformat()
        }
    }), 201


@ratings_bp.route("/clients/<int:client_id>", methods=["GET"])
def get_client_ratings_endpoint(client_id):
    ratings, average, error = get_client_ratings(client_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({
        "client_id": client_id,
        "average_score": average,
        "total_ratings": len(ratings),
        "ratings": [
            {
                "id": r.id,
                "score": r.score,
                "comment": r.comment,
                "user_id": r.user_id,
                "job_id": r.job_id,
                "created_at": r.created_at.isoformat()
            } for r in ratings
        ]
    }), 200