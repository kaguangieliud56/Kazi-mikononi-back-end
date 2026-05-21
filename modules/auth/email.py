import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail


def send_verification_email(to_email, link):

    message = Mail(
        from_email="your_verified_sender@gmail.com",
        to_emails=to_email,
        subject="Verify your account",
        html_content=f"""
            <h2>Verify your account</h2>
            <a href="{link}">Click here to verify</a>
        """
    )

    try:
        sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
        response = sg.send(message)

        print("SendGrid status:", response.status_code)

        return True

    except Exception as e:
        print("SENDGRID ERROR:", str(e))
        return False