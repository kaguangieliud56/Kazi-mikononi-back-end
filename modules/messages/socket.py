from flask_socketio import join_room, emit
from flask_jwt_extended import decode_token
from modules.messages.service import send_message
from extensions import socketio


def get_room_name(user_id_1, user_id_2):
    return f"chat_{min(user_id_1, user_id_2)}_{max(user_id_1, user_id_2)}"


# -----------------------------
# JOIN CHAT
# -----------------------------
@socketio.on("join_chat")
def handle_join_chat(data):

    try:
        token = data.get("token")
        other_user_id = data.get("other_user_id")

        if not token or not other_user_id:
            return

        other_user_id = int(other_user_id)

        decoded = decode_token(token)
        current_user_id = int(decoded["sub"])

        room = get_room_name(current_user_id, other_user_id)

        join_room(room)

        emit("joined_room", {"room": room})

    except Exception as e:
        print("SOCKET JOIN ERROR:", str(e))


# -----------------------------
# SEND MESSAGE
# -----------------------------
@socketio.on("send_message")
def handle_send_message(data):

    try:
        token = data.get("token")
        receiver_id = data.get("receiver_id")
        content = data.get("content")

        if not token or not receiver_id or not content:
            return

        receiver_id = int(receiver_id)

        decoded = decode_token(token)
        sender_id = int(decoded["sub"])

        message, error = send_message(sender_id, {
            "receiver_id": receiver_id,
            "content": content
        })

        if error:
            emit("message_error", {"error": error})
            return

        room = get_room_name(sender_id, receiver_id)

        emit("new_message", {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at.isoformat()
        }, room=room)

    except Exception as e:
        print("SOCKET MESSAGE ERROR:", str(e))