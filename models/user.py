from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # BASIC INFO
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # ROLE SYSTEM (core of your app)
    role = db.Column(db.String(20), nullable=False)
    # client | worker

    # CONTACT / PROFILE INFO
    phone = db.Column(db.String(20), unique=True)
    location = db.Column(db.String(120))
    
    # OPTIONAL WORKER INFO (not duplicated skills here)
    is_verified = db.Column(db.Boolean, default=False)

    # TIMESTAMP
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # RELATIONSHIPS
    jobs = db.relationship("Job", backref="client", lazy=True)

    applications = db.relationship("Application", backref="applicant", lazy=True)

    messages = db.relationship("Message", backref="sender", lazy=True)

    ratings = db.relationship("Rating", backref="user", lazy=True)

    # IMPORTANT: skills handled via WorkerSkill table (NOT here)

    def to_dict(self):
        return {
            "id": self.id,
            "full_name": self.full_name,
            "email": self.email,
            "role": self.role,
            "phone": self.phone,
            "location": self.location,
            "is_verified": self.is_verified,
        }