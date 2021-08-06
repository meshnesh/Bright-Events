import os
from flask_mail import Message
from flask import current_app, make_response, jsonify
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app import mail

SECRET = URLSafeTimedSerializer(os.getenv('SECRET'))


def send_mail(to, subject, html):
    """a function to send emails from the app"""
    msg = Message(sender=current_app.config.get('MAIL_USERNAME'),
                  recipients=[to])
    # os.getenv('MAIL_USERNAME')
    msg.subject = subject
    msg.html = html
    mail.send(msg)
    return "sent"


def confirm_token(salt):
    def wrapper(f):
        def inner(*args, **kwargs):
            try:
                email = SECRET.loads(
                    kwargs['token'], salt=salt,
                    max_age=3600  # token valid for 1 hour
                )
                return f(*args, **kwargs, email=email)

            except SignatureExpired:
                response = {
                    'message': 'The token is expired!, confirm your e-mail again'
                }
                return make_response(jsonify(response)), 401

        return inner

    return wrapper
