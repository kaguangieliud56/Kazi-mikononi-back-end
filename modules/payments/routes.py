from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from modules.payments.service import (
    initiate_stk_push,
    mpesa_callback,
    release_payment,
    get_job_transaction
)

payments_bp = Blueprint("payments", __name__, url_prefix="/payments")


@payments_bp.route("/fund/<int:job_id>", methods=["POST"])
@jwt_required()
def fund_job(job_id):
    client_id = int(get_jwt_identity())
    data = request.get_json()
    phone_number = data.get("phone_number")
    if not phone_number:
        return jsonify({"error": "phone_number is required"}), 400
    transaction, error = initiate_stk_push(client_id, job_id, phone_number)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({
        "message": "STK push sent to your phone. Enter your M-Pesa PIN to complete payment.",
        "transaction_id": transaction.id,
        "amount": transaction.amount,
        "status": transaction.status
    }), 201


@payments_bp.route("/callback", methods=["POST"])
def callback():
    data = request.get_json()
    mpesa_callback(data)
    return jsonify({"ResultCode": 0, "ResultDesc": "Success"}), 200


@payments_bp.route("/release/<int:job_id>", methods=["POST"])
@jwt_required()
def release(job_id):
    client_id = int(get_jwt_identity())
    transaction, error = release_payment(job_id, client_id)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({
        "message": "Payment released to worker successfully",
        "transaction_id": transaction.id,
        "status": transaction.status
    }), 200


@payments_bp.route("/status/<int:job_id>", methods=["GET"])
@jwt_required()
def transaction_status(job_id):
    user_id = int(get_jwt_identity())
    transaction, error = get_job_transaction(job_id, user_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify({
        "job_id": job_id,
        "amount": transaction.amount,
        "status": transaction.status,
        "mpesa_code": transaction.mpesa_code,
        "created_at": transaction.created_at.isoformat()
    }), 200