from flask_mail import Message
from extensions import mail
from flask import current_app


def send_verification_email(user_email, token):

    # -----------------------------------
    # VERIFICATION LINK
    # -----------------------------------
    link = f"http://127.0.0.1:5000/auth/verify/{token}"

    # -----------------------------------
    # CREATE EMAIL MESSAGE
    # -----------------------------------
    msg = Message(
        subject="Verify Your Kazi Mikononi Account",
        sender=current_app.config["MAIL_USERNAME"],
        recipients=[user_email]
    )

    # -----------------------------------
    # PLAIN TEXT VERSION
    # -----------------------------------
    msg.body = f"""
    Welcome to Kazi Mikononi!

    Please verify your email using the link below:

    {link}

    If you did not create this account,
    please ignore this email.
    """

    # -----------------------------------
    # HTML VERSION (MODERN EMAIL UI)
    # -----------------------------------
    msg.html = f"""
    <div style="
        font-family: Arial, sans-serif;
        max-width: 600px;
        margin: auto;
        padding: 40px;
        background-color: #f9fafb;
        border-radius: 12px;
    ">

        <h1 style="
            color: #2563eb;
            text-align: center;
        ">
            Kazi Mikononi
        </h1>

        <h2 style="color: #111827;">
            Verify Your Email
        </h2>

        <p style="
            color: #374151;
            font-size: 16px;
            line-height: 1.6;
        ">
            Thank you for creating your account.
            Please verify your email address
            by clicking the button below.
        </p>

        <div style="text-align:center; margin:40px 0;">

            <a href="{link}" style="text-decoration:none;">

                <button style="
                    background-color:#2563eb;
                    color:white;
                    padding:14px 28px;
                    border:none;
                    border-radius:8px;
                    font-size:16px;
                    font-weight:bold;
                    cursor:pointer;
                ">
                    Verify Email
                </button>

            </a>

        </div>

        <p style="
            color:#6b7280;
            font-size:14px;
            line-height:1.6;
        ">
            If the button does not work,
            copy and paste this link into your browser:
        </p>

        <p style="
            word-break: break-all;
            color:#2563eb;
            font-size:14px;
        ">
            {link}
        </p>

        <hr style="
            margin:40px 0;
            border:none;
            border-top:1px solid #e5e7eb;
        ">

        <p style="
            color:#9ca3af;
            font-size:12px;
            text-align:center;
        ">
            If you did not create this account,
            you can safely ignore this email.
        </p>

    </div>
    """

    # -----------------------------------
    # SEND EMAIL
    # -----------------------------------
    mail.send(msg)