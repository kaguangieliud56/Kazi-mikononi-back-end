from extensions import db


class WorkerAvailability(db.Model):
    __tablename__ = "worker_availability"

    id = db.Column(db.Integer, primary_key=True)

    worker_id = db.Column(db.Integer, db.ForeignKey("users.id"))

    day_of_week = db.Column(db.String(20))  # Monday, Tuesday...

    start_time = db.Column(db.String(10))   # "08:00"
    end_time = db.Column(db.String(10))     # "18:00"