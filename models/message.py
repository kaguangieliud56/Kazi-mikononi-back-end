from extensions import db
from datetime import datetime

class Message(db.Model):
    __tablename__ = "messages"

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # sender
    sender_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # receiver
    receiver_id = db.Column(db.Integer, nullable=False)