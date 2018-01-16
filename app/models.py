"""File contains the db models for application and tables"""

from datetime import datetime, timedelta
from app import db
from flask_bcrypt import Bcrypt
import jwt
from flask import current_app


rsvps = db.Table('rsvps',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id')),
    db.Column('event_id', db.Integer, db.ForeignKey('eventlists.id'))
)


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
    myrsvps = db.relationship('Events', secondary=rsvps,
                              backref=db.backref('rsvpList', lazy='dynamic'), lazy='dynamic')

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

    @staticmethod
    def reset_password():
        """Save a new user user password to the database."""
        db.session.commit()

    @staticmethod
    def generate_token(user_id):
        """ Generates the access token"""

        try:
            # set up a payload with an expiration time
            payload = {
                'exp': datetime.utcnow() + timedelta(minutes=1440),
                'iat': datetime.utcnow(),
                'sub': user_id
            }
            # create the byte string token using the payload and the SECRET key
            jwt_string = jwt.encode(
                payload,
                current_app.config.get('SECRET'),
                algorithm='HS256'
            )
            return jwt_string

        except Exception as error:
            # return an error in string format if an exception occurs
            return str(error)

    @staticmethod
    def decode_token(token):
        """Decodes the access token from the Authorization header."""
        try:
            # try to decode the token using our SECRET variable
            payload = jwt.decode(token, current_app.config.get('SECRET'))
            return payload['sub']
        except jwt.ExpiredSignatureError:
            # the token is expired, return an error string
            return "Expired token. Please login to get a new token"
        except jwt.InvalidTokenError:
            # the token is invalid, return an error string
            return "Invalid token. Please register or login"

    def __str__(self):
        return """User(id={}, name={}, email={}, events={})""".format(
            self.id, self.name, self.email, self.myrsvps.all())

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
    created_by = db.Column(db.Integer, db.ForeignKey(User.id))

    def __init__(self, title, location, time, date, description, cartegory, imageUrl, created_by):
        """initialize an event with its creator."""
        self.title = title
        self.location = location
        self.time = time
        self.date = date
        self.description = description
        self.cartegory = cartegory
        self.imageUrl = imageUrl
        self.created_by = created_by

    def save(self):
        """Save an event to the database.
        This includes creating a new event and editing one.
        """
        db.session.add(self)
        db.session.commit()

    def add_rsvp(self, user):
        """ This method adds a user to the list of rsvps"""
        #check if the user is already in the list
        evt = user.myrsvps.filter_by(id=self.id).first()
        if evt:
            return True
        self.rsvpList.append(user)
        db.session.add(user)
        db.session.commit()
        return False

    @staticmethod
    def get_all_user(user_id):
        """This method gets all the events for a given user."""
        return Events.query.filter_by(created_by=user_id)

    @staticmethod
    def get__all_events():
        """This method gets all the events in the db"""
        return Events.query.all()

    def delete(self):
        """This method deletes a given event."""
        db.session.delete(self)
        db.session.commit()

    def __str__(self):
        return "<Events: {}>".format(self.title)

    __repr__ = __str__


class BlacklistToken(db.Model):
    """
    Token Model for storing JWT tokens
    """
    __tablename__ = 'blacklist_tokens'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    token = db.Column(db.String(500), unique=True, nullable=False)
    blacklisted_on = db.Column(db.DateTime, nullable=False)

    def __init__(self, token):
        self.token = token
        self.blacklisted_on = datetime.datetime.now()

    def __repr__(self):
        return '<id: token: {}'.format(self.token)
