from extensions import db
from models.message import Message
from models.user import User

def send_message(sender_id, data):
    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id or not content:
        return None, "receiver_id and content are required"

    receiver = User.query.get(receiver_id)
    if not receiver:
        return None, "Receiver not found"

    if sender_id == receiver_id:
        return None, "You cannot message yourself"

    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    return message, None

def get_conversation(user_id, other_user_id):
    other = User.query.get(other_user_id)
    if not other:
        return None, "User not found"

    messages = Message.query.filter(
        db.or_(
            db.and_(
                Message.sender_id == user_id,
                Message.receiver_id == other_user_id
            ),
            db.and_(
                Message.sender_id == other_user_id,
                Message.receiver_id == user_id
            )
        )
    ).order_by(Message.created_at.asc()).all()
    return messages, None

def get_my_conversations(user_id):
    messages = Message.query.filter(
        db.or_(
            Message.sender_id == user_id,
            Message.receiver_id == user_id
        )
    ).order_by(Message.created_at.desc()).all()

    seen = set()
    conversations = []
    for m in messages:
        other_id = m.receiver_id if m.sender_id == user_id else m.sender_id
        if other_id not in seen:
            seen.add(other_id)
            conversations.append({
                "other_user_id": other_id,
                "last_message": m.content,
                "created_at": m.created_at.isoformat()
            })
    return conversations