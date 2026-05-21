from sqlalchemy.exc import IntegrityError
from models.user import User
from models.skill import Skill
from models.worker_skill import WorkerSkill
from models.worker_profile import WorkerProfile
from extensions import db
from modules.auth.utils import hash_password, verify_password
from flask_jwt_extended import create_access_token
from blacklist import BLACKLIST
from itsdangerous import URLSafeTimedSerializer
from itsdangerous.exc import SignatureExpired, BadSignature
from flask import current_app
from modules.auth.email import send_verification_email
from datetime import timedelta


# =====================================================
# TOKEN GENERATION
# =====================================================
def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="email-confirm")


# =====================================================
# VERIFY EMAIL
# =====================================================
def verify_email(token):

    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])

    try:
        email = serializer.loads(
            token,
            salt="email-confirm",
            max_age=3600
        )

        user = User.query.filter_by(email=email).first()

        if not user:
            return {"error": "User not found"}, 404

        if user.is_verified:
            return {"message": "Email already verified"}, 200

        user.is_verified = True
        db.session.commit()

        return {"message": "Email verified successfully"}, 200

    except SignatureExpired:
        return {"error": "Verification link expired"}, 400

    except BadSignature:
        return {"error": "Invalid verification token"}, 400


# =====================================================
# REGISTER USER (YOUR CODE + FIXED EMAIL LINK)
# =====================================================
def register_user(data):

    try:
        required_fields = ["full_name", "email", "password", "role"]

        for field in required_fields:
            if not data.get(field):
                return {"error": f"{field} is required"}, 400

        existing = User.query.filter_by(email=data["email"]).first()

        if existing:
            return {"error": "Email already exists"}, 400

        allowed_roles = ["worker", "client"]

        if data["role"] not in allowed_roles:
            return {"error": "Invalid role"}, 400

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
            is_verified=False
        )

        db.session.add(user)
        db.session.flush()

        # -------------------------
        # WORKER PROFILE
        # -------------------------
        if user.role == "worker":

            existing_profile = WorkerProfile.query.filter_by(user_id=user.id).first()

            if not existing_profile:
                worker_profile = WorkerProfile(user_id=user.id)
                db.session.add(worker_profile)

        db.session.commit()

        # =====================================================
        # EMAIL VERIFICATION (FIXED FOR RENDER DEPLOYMENT)
        # =====================================================

        token = generate_token(user.email)

        # 🔥 IMPORTANT FIX: USE YOUR DEPLOYED BACKEND URL
        verification_link = (
            f"https://kazi-mikononi-back-end.onrender.com/auth/verify/{token}"
        )

        email_sent = send_verification_email(user.email, verification_link)

        if not email_sent:
            return {
                "error": "User created but verification email failed to send"
            }, 500

        # =====================================================
        # LOGIN TOKEN (YOU KEPT THIS - NOT REMOVED)
        # =====================================================

        access_token = create_access_token(
            identity=str(user.id),
            expires_delta=timedelta(days=7)
        )

        return {
            "message": "User created successfully. Please verify your email.",
            "token": access_token,
            "user": user.to_dict()
        }, 201

    except IntegrityError:
        db.session.rollback()

        return {
            "error": "Database constraint violation (email or phone already exists)"
        }, 400

    except Exception as e:
        db.session.rollback()

        print("REGISTER ERROR:", str(e))

        return {
            "error": "Internal server error",
            "details": str(e)
        }, 500


# =====================================================
# LOGIN USER (UNCHANGED LOGIC)
# =====================================================
def login_user(data):

    try:
        if not data.get("email") or not data.get("password"):
            return {"error": "email and password are required"}, 400

        user = User.query.filter_by(email=data["email"]).first()

        if not user:
            return {"error": "Invalid credentials"}, 401

        # EMAIL CHECK (YOU ALREADY HAD THIS GOOD)
        if not user.is_verified:
            return {"error": "Please verify your email before logging in"}, 403

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


# =====================================================
# LOGOUT USER (UNCHANGED)
# =====================================================
def logout_user(jwt_data):

    jti = jwt_data["jti"]
    BLACKLIST.add(jti)

    return {
        "message": "Logged out successfully"
    }, 200