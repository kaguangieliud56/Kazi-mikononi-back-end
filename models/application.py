from extensions import db
from datetime import datetime

class Application(db.Model):
    __tablename__ = "applications"

    id = db.Column(db.Integer, primary_key=True)

    message = db.Column(db.Text, nullable=True)

    status = db.Column(db.String(20), default="pending")
    # pending | accepted | rejected

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 relationships
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)