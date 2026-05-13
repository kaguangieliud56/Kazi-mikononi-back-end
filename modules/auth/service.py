from sqlalchemy.exc import IntegrityError
from models.user import User
from models.skill import Skill
from models.worker_skill import WorkerSkill
from models.worker_profile import WorkerProfile
from extensions import db
from modules.auth.utils import hash_password, verify_password
from flask_jwt_extended import create_access_token


def register_user(data):

    try:
        # -------------------------
        # BASIC VALIDATION
        # -------------------------
        required_fields = ["full_name", "email", "password", "role"]

        for field in required_fields:
            if not data.get(field):
                return {"error": f"{field} is required"}, 400

        # -------------------------
        # CHECK EXISTING USER
        # -------------------------
        existing = User.query.filter_by(email=data["email"]).first()
        if existing:
            return {"error": "Email already exists"}, 400

        # -------------------------
        # CREATE USER
        # -------------------------
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
        db.session.flush()

        # -------------------------
        # WORKER PROFILE
        # -------------------------
        if user.role == "worker":

            worker_profile = WorkerProfile(user_id=user.id)
            db.session.add(worker_profile)
            db.session.flush()

            skills = data.get("skills", [])

            for skill_name in skills:

                skill = Skill.query.filter_by(name=skill_name).first()

                if not skill:
                    skill = Skill(name=skill_name)
                    db.session.add(skill)
                    db.session.flush()

                worker_skill = WorkerSkill(
                    worker_id=worker_profile.id,
                    skill_id=skill.id
                )

                db.session.add(worker_skill)

        # -------------------------
        # COMMIT
        # -------------------------
        db.session.commit()

        token = create_access_token(identity=str(user.id))

        return {
            "message": "User created successfully",
            "token": token,
            "user": user.to_dict()
        }, 201

    # -------------------------
    # HANDLE UNIQUE CONSTRAINTS
    # -------------------------
    except IntegrityError as e:
        db.session.rollback()

        return {
            "error": "Database constraint violation (email or phone already exists)"
        }, 400

    # -------------------------
    # HANDLE GENERAL ERRORS
    # -------------------------
    except Exception as e:
        db.session.rollback()

        return {
            "error": "Internal server error",
            "details": str(e)
        }, 500


def login_user(data):

    try:
        if not data.get("email") or not data.get("password"):
            return {"error": "email and password are required"}, 400

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

    except Exception as e:
        return {
            "error": "Login failed",
            "details": str(e)
        }, 500