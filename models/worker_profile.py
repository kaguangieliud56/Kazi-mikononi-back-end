from extensions import db

class WorkerProfile(db.Model):
    __tablename__ = "worker_profiles"

    id = db.Column(db.Integer, primary_key=True)

    bio = db.Column(db.Text, nullable=True)

    experience_years = db.Column(db.Integer, default=0)

    availability = db.Column(db.String(50), default="available")

    # link to user
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)