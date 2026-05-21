from extensions import db

from models.message import Message
from models.user import User
from models.conversation import Conversation

from sqlalchemy import or_


# =========================================
# CREATE OR GET CONVERSATION
# =========================================
def get_or_create_conversation(user1_id, user2_id):

    conversation = Conversation.query.filter(

        (
            (Conversation.user1_id == user1_id) &
            (Conversation.user2_id == user2_id)
        )

        |

        (
            (Conversation.user1_id == user2_id) &
            (Conversation.user2_id == user1_id)
        )

    ).first()

    # already exists
    if conversation:
        return conversation

    # create new
    conversation = Conversation(
        user1_id=user1_id,
        user2_id=user2_id
    )

    db.session.add(conversation)
    db.session.commit()

    return conversation


# =========================================
# SEND MESSAGE
# =========================================
def send_message(sender_id, data):

    receiver_id = data.get("receiver_id")
    content = data.get("content")

    if not receiver_id or not content:
        return None, "Missing fields"

    # get chat room
    conversation = get_or_create_conversation(
        sender_id,
        receiver_id
    )

    # create message
    message = Message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        conversation_id=conversation.id,
        content=content
    )

    db.session.add(message)
    db.session.commit()

    return message, None


# =========================================
# GET CONVERSATION MESSAGES
# =========================================
def get_conversation(user_id, other_user_id):

    conversation = get_or_create_conversation(
        user_id,
        other_user_id
    )

    messages = Message.query.filter_by(
        conversation_id=conversation.id
    ).order_by(
        Message.created_at.asc()
    ).all()

    return messages, None


# =========================================
# GET CONTACT LIST / SIDEBAR
# =========================================
def get_my_conversations(user_id):

    conversations = Conversation.query.filter(

        (Conversation.user1_id == user_id)

        |

        (Conversation.user2_id == user_id)

    ).order_by(
        Conversation.created_at.desc()
    ).all()

    result = []

    for conversation in conversations:

        # determine other user
        other_user_id = (
            conversation.user2_id
            if conversation.user1_id == user_id
            else conversation.user1_id
        )

        # fetch user info
        other_user = User.query.get(other_user_id)

        # latest message
        last_message = Message.query.filter_by(
            conversation_id=conversation.id
        ).order_by(
            Message.created_at.desc()
        ).first()

        result.append({

            "conversation_id": conversation.id,

            "other_user_id": other_user_id,

            "name": (
                other_user.name
                if other_user
                else f"User {other_user_id}"
            ),

            "avatar": (
                other_user.profile_image
                if other_user and hasattr(other_user, "profile_image")
                else None
            ),

            "last_message": (
                last_message.content
                if last_message
                else ""
            ),

            "created_at": conversation.created_at.isoformat()

        })

    return {
        "conversations": result
    }