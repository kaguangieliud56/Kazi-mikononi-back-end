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
from modules.auth.resend_email import send_verification_email

def generate_token(email):
    serializer = URLSafeTimedSerializer(current_app.config["SECRET_KEY"])
    return serializer.dumps(email, salt="email-confirm")

def verify_email(token):

    serializer = URLSafeTimedSerializer(
        current_app.config["SECRET_KEY"]
    )

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
            return {
                "message": "Email already verified"
            }, 200

        user.is_verified = True

        db.session.commit()

        return {
            "message": "Email verified successfully"
        }, 200

    except SignatureExpired:
        return {
            "error": "Verification link expired"
        }, 400

    except BadSignature:
        return {
            "error": "Invalid verification token"
        }, 400
    
    
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


        allowed_roles = ["worker", "client"]

        if data["role"] not in allowed_roles:
            return {
                "error": "Invalid role"
            }, 400

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
            bio=data.get("bio"),

            # 🔥 EMAIL NOT VERIFIED YET
            is_verified=False
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

            

        # -------------------------
        # COMMIT TO DATABASE
        # -------------------------
        db.session.commit()

        # -------------------------
        # GENERATE EMAIL VERIFICATION TOKEN
        # -------------------------
        verification_token = generate_token(user.email)

        # -------------------------
        # SEND EMAIL
        # -------------------------
        try:
            send_verification_email(user.email, verification_token)
        except Exception as e:
            print("EMAIL FAILED:", str(e))

        # -------------------------
        # CREATE LOGIN TOKEN
        # -------------------------
        access_token = create_access_token(
            identity=str(user.id)
        )

        return {
            "message": "User created successfully. Please verify your email.",
            "token": access_token,
            "user": user.to_dict()
        }, 201

    # -------------------------
    # HANDLE UNIQUE CONSTRAINTS
    # -------------------------
    except IntegrityError:
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
    """
    Handles user login:
    - validates input
    - checks if user exists
    - verifies password
    - returns JWT token + user data
    """

    try:
        # -------------------------------
        # 1. Validate input data
        # -------------------------------
        if not data.get("email") or not data.get("password"):
            return {"error": "email and password are required"}, 400

        # -------------------------------
        # 2. Find user by email
        # -------------------------------
        user = User.query.filter_by(email=data["email"]).first()

        if not user:
            return {"error": "Invalid credentials"}, 401

        # -------------------------------
        # 3. EMAIL VERIFICATION CHECK (DISABLED FOR DEV)
        # -------------------------------
        # Commented out for development/testing purposes
        # Remove this block so users can log in without verifying email

        # if not user.is_verified:
        #     return {
        #         "error": "Please verify your email before logging in"
        #     }, 403

        # -------------------------------
        # 4. Verify password
        # -------------------------------
        if not verify_password(user.password_hash, data["password"]):
            return {"error": "Invalid credentials"}, 401

        # -------------------------------
        # 5. Create JWT token
        # -------------------------------
        token = create_access_token(identity=str(user.id))

        # -------------------------------
        # 6. Return success response
        # -------------------------------
        return {
            "message": "Login successful",
            "token": token,
            "user": user.to_dict()
        }, 200

    except Exception as e:
        # -------------------------------
        # 7. Catch unexpected errors
        # -------------------------------
        return {
            "error": "Login failed",
            "details": str(e)
        }, 500

def logout_user(jwt_data):

    jti = jwt_data["jti"]

    BLACKLIST.add(jti)

    return {
        "message": "Logged out successfully"
    }, 200