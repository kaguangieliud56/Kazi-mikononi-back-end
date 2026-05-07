from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    full_name = db.Column(db.String(120), nullable=False)

    email = db.Column(db.String(120), unique=True, nullable=False)

    password = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), nullable=False)  
    # roles: client | worker

    phone = db.Column(db.String(20), unique=True, nullable=True)

    location = db.Column(db.String(120), nullable=True)

    profile_image = db.Column(db.String(255), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔗 RELATIONSHIPS (IMPORTANT)

    jobs = db.relationship("Job", backref="client", lazy=True)

    applications = db.relationship("Application", backref="applicant", lazy=True)

    messages = db.relationship("Message", backref="sender", lazy=True)

    ratings = db.relationship("Rating", backref="user", lazy=True)