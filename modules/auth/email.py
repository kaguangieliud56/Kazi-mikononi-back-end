from flask_mail import Message
from extensions import mail
from flask import current_app


def send_verification_email(user_email, token):
    print("EMAIL SKIPPED (production safe mode)")

    link = f"https://kazi-mikononi-back-end.onrender.com/auth/verify/{token}"

    print("Verification link:", link)