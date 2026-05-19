from extensions import db
from datetime import datetime

class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    budget = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)

    # NEW 👇 job image
    image_url = db.Column(db.String(500), nullable=True)

    status = db.Column(db.String(20), default="open")
    # open | in_progress | completed

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    applications = db.relationship(
        "Application",
        backref="job",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):
        from models.user import User

        client = User.query.get(self.client_id)

        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "budget": self.budget,
            "location": self.location,
            "status": self.status,
            "image_url": self.image_url,   # 👈 ADD THIS

            "client_id": self.client_id,
            "employer": client.full_name if client else "Unknown",
            "applicants": len(self.applications),
            "created_at": self.created_at.isoformat()
        }