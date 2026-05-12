from models.user import User
from models.skill import Skill
from models.worker_skill import WorkerSkill
from extensions import db
from modules.auth.utils import hash_password
from flask_jwt_extended import create_access_token
from modules.auth.utils import hash_password, verify_password

def register_user(data):

    existing = User.query.filter_by(email=data["email"]).first()

    if existing:
        return {"error": "Email already exists"}, 400

    user = User(
        full_name=data["full_name"],
        email=data["email"],
        password_hash=hash_password(data["password"]),
        role=data["role"],
        phone=data.get("phone"),
        location=data.get("location"),
        bio=data.get("bio")
    )

    db.session.add(user)
    db.session.flush()  # get user.id before commit

    # 👇 ONLY WORKERS GET SKILLS
    if user.role == "worker":

        skills = data.get("skills", [])

        for skill_name in skills:

            skill = Skill.query.filter_by(name=skill_name).first()

            if not skill:
                skill = Skill(name=skill_name)
                db.session.add(skill)
                db.session.flush()

            worker_skill = WorkerSkill(
                worker_id=user.id,
                skill_id=skill.id
            )

            db.session.add(worker_skill)

    db.session.commit()

    token = create_access_token(identity=str(user.id))

    return {
        "message": "User created successfully",
        "token": token,
        "user": user.to_dict()
    }, 201


def login_user(data):

    user = User.query.filter_by(email=data["email"]).first()

    if not user:
        return {"error": "Invalid credentials"}, 401

    if not verify_password(user.password_hash, data["password"]):
        return {"error": "Invalid credentials"}, 401

    token = create_access_token(identity=str(user.id))

    return {
        "message": "Login successful",
        "token": token,
        "user": user.to_dict()
    }, 200