from extensions import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)

    description = db.Column(db.Text, nullable=False)

    budget = db.Column(db.Float, nullable=False)

    location = db.Column(db.String(120), nullable=False)

    status = db.Column(db.String(20), default="open")
    # open | in_progress | completed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 Foreign Key → User (client)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # relationships
    applications = db.relationship("Application", backref="job", lazy=True)