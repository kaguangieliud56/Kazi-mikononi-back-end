from extensions import db

class Skill(db.Model):
    __tablename__ = "skills"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)

    worker_skills = db.relationship("WorkerSkill", backref="skill", lazy=True)

    worker_skills = db.relationship(
    "WorkerSkill",
    back_populates="skill",
    cascade="all, delete-orphan"
)

    def to_dict(self):

        return {
            "id": self.id,
            "name": self.name
        }