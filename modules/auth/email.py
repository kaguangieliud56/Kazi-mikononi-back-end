import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def send_verification_email(to_email, link):
    message = Mail(
        from_email='your_verified_sender@gmail.com',
        to_emails=to_email,
        subject='Verify your account',
        html_content=f'''
            <h2>Verify your account</h2>
            <p>Click below to verify:</p>
            <a href="{link}">Verify Email</a>
        '''
    )

    try:
        sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg.send(message)
        print("Email sent!")
    except Exception as e:
        print("Error:", e)