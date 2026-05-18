import requests
import os

def send_verification_email(user_email, token):
    try:
        backend_url = os.getenv("BACKEND_URL")

        link = f"{backend_url}/auth/verify/{token}"

        response = requests.post(
            "https://api.resend.com/emails",
            headers={
                "Authorization": f"Bearer {os.getenv('RESEND_API_KEY')}",
                "Content-Type": "application/json"
            },
            json={
                "from": os.getenv("MAIL_DEFAULT_SENDER"),
                "to": [user_email],
                "subject": "Verify your account",
                "html": f"""
                    <h2>Verify Your Account</h2>
                    <p>Click the link below:</p>
                    <a href="{link}">Verify Email</a>
                """
            }
        )

        print("EMAIL STATUS:", response.status_code, response.text)

    except Exception as e:
        print("EMAIL FAILED:", str(e))