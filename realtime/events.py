from flask_socketio import emit, join_room, leave_room
from extensions import db
from models.message import Message

def handle_events(socketio):

    @socketio.on("connect")
    def on_connect():
        print("Client connected")
        emit("connected", {"message": "Connected to Kazi Mikononi realtime server"})

    @socketio.on("disconnect")
    def on_disconnect():
        print("Client disconnected")

    @socketio.on("join")
    def on_join(data):
        room = data.get("room")
        if room:
            join_room(room)
            emit("joined", {"message": f"Joined room {room}"}, room=room)

    @socketio.on("leave")
    def on_leave(data):
        room = data.get("room")
        if room:
            leave_room(room)
            emit("left", {"message": f"Left room {room}"}, room=room)

    @socketio.on("send_message")
    def on_send_message(data):
        sender_id = data.get("sender_id")
        receiver_id = data.get("receiver_id")
        content = data.get("content")

        if not sender_id or not receiver_id or not content:
            emit("error", {"message": "sender_id, receiver_id and content are required"})
            return

        message = Message(
            sender_id=sender_id,
            receiver_id=receiver_id,
            content=content
        )
        db.session.add(message)
        db.session.commit()

        room = f"chat_{min(sender_id, receiver_id)}_{max(sender_id, receiver_id)}"

        emit("new_message", {
            "id": message.id,
            "sender_id": message.sender_id,
            "receiver_id": message.receiver_id,
            "content": message.content,
            "created_at": message.created_at.isoformat()
        }, room=room)