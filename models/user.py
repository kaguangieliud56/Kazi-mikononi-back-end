from extensions import db
from datetime import datetime


class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # BASIC INFO
    full_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)

    # ROLE
    role = db.Column(db.String(20), nullable=False)

    # CONTACT / PROFILE
    phone = db.Column(db.String(20), unique=True)
    location = db.Column(db.String(120))
    is_verified = db.Column(db.Boolean, default=False)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # =========================
    # RELATIONSHIPS (FIXED)
    # =========================

    jobs = db.relationship("Job", back_populates="client")

    applications = db.relationship("Application", backref="applicant", lazy=True)

    ratings = db.relationship("Rating", backref="user", lazy=True)

    # MESSAGES (IMPORTANT FIX)
    sent_messages = db.relationship(
        "Message",
        foreign_keys="Message.sender_id",
        back_populates="sender",
        lazy=True
    )

    received_messages = db.relationship(
        "Message",
        foreign_keys="Message.receiver_id",
        back_populates="receiver",
        lazy=True
    )

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