from app import db
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
import jwt
from datetime import datetime, timedelta
from flask import current_app, Flask


class User(db.Model):
    """This class defines the users table """

    __tablename__ = 'users'

    # Define the columns of the users table, starting with the primary key
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(256), nullable=False)
    email = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256))
    eventlists = db.relationship(
        'Events', order_by='Events.id', cascade="all, delete-orphan")

    def __init__(self, name, email, password):
        """Initialize the user with a name, an email and a password."""
        self.name = name
        self.email = email
        self.password = Bcrypt().generate_password_hash(password).decode()

    def password_is_valid(self, password):
        """
        Checks the password against it's hash to validates the user's password
        """
        return Bcrypt().check_password_hash(self.password, password)


    def save(self):
        """Save a user to the database.
        This includes creating a new user and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def __str__(self):
        return """User(id={}, name={}, email={}, events={})""".format(self.id, self.name, self.email)

    __repr__ = __str__


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
    imageUrl = db.Column(db.String(255))

    def __init__(self, title, location, time, date, description, cartegory, imageUrl):
        """initialize an event with its creator."""
        self.title = title
        self.location = location
        self.time = time
        self.date = date
        self.description = description
        self.cartegory = cartegory
        self.imageUrl = imageUrl

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