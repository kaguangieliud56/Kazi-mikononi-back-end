from extensions import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = "transactions"

    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey("jobs.id"), nullable=False)
    client_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")
    # pending | funded | released | refunded
    mpesa_code = db.Column(db.String(50), nullable=True)
    checkout_request_id = db.Column(db.String(100), nullable=True)
    phone_number = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)