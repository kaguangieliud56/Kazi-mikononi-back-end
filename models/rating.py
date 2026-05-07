from extensions import db
from datetime import datetime

class Rating(db.Model):
    __tablename__ = "ratings"

    id = db.Column(db.Integer, primary_key=True)

    score = db.Column(db.Integer, nullable=False)
    # 1 - 5 stars

    comment = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # who gives rating
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # who receives rating
    worker_id = db.Column(db.Integer, nullable=False)