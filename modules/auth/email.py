from flask_mail import Message
from extensions import mail
from flask import current_app


def send_verification_email(user_email, token):
    try:
        link = f"https://kazi-mikononi-back-end.onrender.com/auth/verify/{token}"

        msg = Message(
            subject="Verify Your Account",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[user_email]
        )

        msg.body = f"Verify here: {link}"

        mail.send(msg)

    except Exception as e:
        print("EMAIL FAILED (non-blocking):", str(e))