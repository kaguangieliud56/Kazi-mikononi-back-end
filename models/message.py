from extensions import db
from datetime import datetime


class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    conversation_id = db.Column(
        db.Integer,
        db.ForeignKey("conversations.id"),
        nullable=False
    )

    # =========================
    # RELATIONSHIPS (FIXED)
    # =========================

    sender = db.relationship(
        "User",
        foreign_keys=[sender_id],
        back_populates="sent_messages"
    )

    receiver = db.relationship(
        "User",
        foreign_keys=[receiver_id],
        back_populates="received_messages"
    )

    conversation = db.relationship("Conversation", back_populates="messages")