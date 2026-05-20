from extensions import db
from datetime import datetime

class WorkerProfile(db.Model):

    __tablename__ = "worker_profiles"

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    title = db.Column(db.String(120))

    phone = db.Column(db.String(20))

    bio = db.Column(db.Text)

    experience_years = db.Column(db.Integer)

    hourly_rate = db.Column(db.Float)

    profile_image = db.Column(db.String(255))

    profile_completed = db.Column(
        db.Boolean,
        default=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    skills = db.relationship(
        "WorkerSkill",
        backref="worker_profile",
        lazy=True
    )

    def to_dict(self):

        return {
            "id": self.id,
            "user_id": self.user_id,
            "title": self.title,
            "phone": self.phone,
            "bio": self.bio,
            "experience_years": self.experience_years,
            "hourly_rate": self.hourly_rate,
            "profile_image": self.profile_image,
            "profile_completed": self.profile_completed
        }