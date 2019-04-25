from appthings import inicializApp
from flask import current_app
from flask_mail import Message


def send_email(to, subject, template):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=current_app.config['MAIL_DEFAULT_SENDER']
    )
    inicializApp.mailn.send(msg)


