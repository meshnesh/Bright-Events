import os
from flask_mail import Message
from flask import current_app
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app import mail

SECRET = URLSafeTimedSerializer(os.getenv('SECRET'))

def send_mail(to, subject, html):
	"""a function to send emails from the app"""
	msg = Message(sender = current_app.config.get('MAIL_USERNAME'),
		recipients = [to])
	msg.subject = subject
	msg.html = html
	mail.send(msg)
	return "sent"

def confirm_token(token, ss):
	return SECRET.loads(
		token, salt=ss,
		max_age=3600 # token valid for 1 hour
	)