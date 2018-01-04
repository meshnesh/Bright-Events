from app import db
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta
from flask import current_app, Flask

class Events(db.Model):
    """This class represents the eventlist table."""

    __tablename__ = 'eventlists'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(50), nullable=False, unique=True)
    location = db.Column(db.String(50), nullable=False)
    time = db.Column(db.String(255), nullable=False)
    date = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    cartegory = db.Column(db.String(255), nullable=False)

    def __init__(self, title, location, time, date, description, cartegory):
        """initialize an event with its creator."""
        self.title = title
        self.location = location
        self.time = time
        self.date = date
        self.description = description
        self.cartegory = cartegory

    def save(self):
        db.session.add(self)
        db.session.commit()

    def add_rsvp(self, user):
        # print(user)
        """ This method adds a user to the list of rsvps"""
        evt = user.myrsvps.filter_by(id=self.id).first()
        if evt:
            return True
        self.rsvpList.append(user)
        db.session.add(user)
        db.session.commit()
        return False

    def get__all_rsvp(self, user):
        """This method gets all the events for a given user."""
        # return Events.query.filter_by(created_by=user_id)
        for user in self.rsvpList:
            # print(user)
            return user

    @staticmethod
    def get_all_user(user_id):
        """This method gets all the events for a given user."""
        return Events.query.filter_by(created_by=user_id)

    @staticmethod
    def get__all_events():
        """This method gets all the events for a given user."""
        # return Events.query.filter_by(created_by=user_id)
        return Events.query.all()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return "<Events: {}>".format(self.title) # check on this later

    __repr__ = __str__