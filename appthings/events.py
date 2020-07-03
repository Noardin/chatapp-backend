from appthings import inicializApp
from flask import current_app
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import os


def send_email(to, subject, template):
    message = Mail(
        from_email=current_app.config['MAIL_DEFAULT_SENDER'],
        to_emails=to,
        subject=subject,
        html_content=template

    )
    try:
        sg = SendGridAPIClient(os.environ['SENDGRID_API_KEY'])
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e)
        print(e.body)


