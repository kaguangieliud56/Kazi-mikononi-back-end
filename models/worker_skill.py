from extensions import db

class WorkerSkill(db.Model):
    __tablename__ = "worker_skills"

    id = db.Column(db.Integer, primary_key=True)

    worker_id = db.Column(db.Integer, db.ForeignKey("worker_profiles.id"))

    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"))