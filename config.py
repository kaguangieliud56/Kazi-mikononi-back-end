import os
from dotenv import load_dotenv
from datetime import timedelta

load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(days=7)

    # -------------------------
    # MAIL CONFIG
    # -------------------------
    RESEND_API_KEY = os.getenv("RESEND_API_KEY")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    FRONTEND_URL = os.getenv("FRONTEND_URL")
    BACKEND_URL = os.getenv("BACKEND_URL")

    # -------------------------
    # IMAGE UPLOADS
    # -------------------------
    UPLOAD_FOLDER = os.path.join(BASE_DIR, "static/uploads")

    MAX_CONTENT_LENGTH = 5 * 1024 * 1024

    # -------------------------
    # MPESA CONFIG
    # -------------------------
    MPESA_CONSUMER_KEY = os.getenv("MPESA_CONSUMER_KEY")
    MPESA_CONSUMER_SECRET = os.getenv("MPESA_CONSUMER_SECRET")
    MPESA_SHORTCODE = os.getenv("MPESA_SHORTCODE")
    MPESA_PASSKEY = os.getenv("MPESA_PASSKEY")
    MPESA_CALLBACK_URL = os.getenv("MPESA_CALLBACK_URL")