from extensions import db

class WorkerSkill(db.Model):
    __tablename__ = "worker_skills"

    id = db.Column(db.Integer, primary_key=True)

    worker_id = db.Column(db.Integer, db.ForeignKey("worker_profiles.id"), nullable=False)
    skill_id = db.Column(db.Integer, db.ForeignKey("skills.id"), nullable=False)

    __table_args__ = (
        db.UniqueConstraint("worker_id", "skill_id", name="unique_worker_skill"),
    )
    
    skill = db.relationship(
    "Skill",
    backref="worker_skills"
)