from extensions import db
from datetime import datetime


class Job(db.Model):
    __tablename__ = "jobs"

    id = db.Column(db.Integer, primary_key=True)

    # core info
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)

    # job meta
    category = db.Column(db.String(50), nullable=True)

    budget = db.Column(db.Float, nullable=False)
    location = db.Column(db.String(120), nullable=False)

    status = db.Column(db.String(20), default="open")
    # open | in_progress | completed

    # extra frontend fields
    urgency = db.Column(db.String(50), default="Flexible - No rush")
    duration = db.Column(db.String(50), default="Few hours")
    contact_method = db.Column(db.String(50), default="Platform Messages")

    # image upload / url
    image_url = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # foreign key
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    # relationships
    applications = db.relationship("Application", backref="job", lazy=True)

    client = db.relationship("User", backref="jobs")

    def to_dict(self):
        from models.user import User

        client = User.query.get(self.client_id)

        return {
            # core
            "id": self.id,
            "title": self.title,
            "description": self.description,

            # job classification
            "category": self.category,

            # financial + location
            "budget": self.budget,
            "location": self.location,

            # status
            "status": self.status,

            # extra job details (frontend form fields)
            "urgency": self.urgency,
            "duration": self.duration,
            "contact_method": self.contact_method,

            # media
            "image_url": self.image_url,

            # relations
            "client_id": self.client_id,
            "employer": client.full_name if client else "Unknown",

            # computed
            "applicants": len(self.applications),

            # timestamp
            "created_at": self.created_at.isoformat()
        }