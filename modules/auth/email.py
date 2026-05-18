from flask_mail import Message
from extensions import mail
from flask import current_app


def send_verification_email(user_email, token):

    try:

        link = f"https://kazi-mikononi-back-end.onrender.com/auth/verify/{token}"

        msg = Message(
            subject="Verify Your Kazi Mikononi Account",
            sender=current_app.config["MAIL_DEFAULT_SENDER"],
            recipients=[user_email]
        )

        msg.body = f"""
        Verify your email:

        {link}
        """

        msg.html = f"""
        <h2>Verify Email</h2>

        <a href="{link}">
            Verify Account
        </a>
        """

        mail.send(msg)

        print("EMAIL SENT SUCCESSFULLY")

    except Exception as e:

        print("EMAIL FAILED")
        print(str(e))