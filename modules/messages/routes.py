from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from modules.messages.service import (
    send_message,
    get_conversation,
    get_my_conversations
)

messages_bp = Blueprint("messages", __name__, url_prefix="/messages")


@messages_bp.route("/", methods=["POST"])
@jwt_required()
def send():
    sender_id = int(get_jwt_identity())
    data = request.get_json()
    message, error = send_message(sender_id, data)
    if error:
        return jsonify({"error": error}), 400
    return jsonify({
        "message": "Message sent successfully",
        "data": {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at.isoformat()
        }
    }), 201


@messages_bp.route("/<int:other_user_id>", methods=["GET"])
@jwt_required()
def conversation(other_user_id):
    user_id = int(get_jwt_identity())
    messages, error = get_conversation(user_id, other_user_id)
    if error:
        return jsonify({"error": error}), 404
    return jsonify([
        {
            "id": m.id,
            "sender_id": m.sender_id,
            "receiver_id": m.receiver_id,
            "content": m.content,
            "created_at": m.created_at.isoformat()
        } for m in messages
    ]), 200


@messages_bp.route("/conversations", methods=["GET"])
@jwt_required()
def conversations():
    user_id = int(get_jwt_identity())
    result = get_my_conversations(user_id)
    return jsonify(result), 200