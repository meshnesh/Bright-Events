# -*- coding: utf-8 -*-
"""import depancies."""
import re
from flask import abort
from flask_restful import reqparse, Api, Resource, fields, marshal
from flasgger import Swagger
from app import app

from app.data import EVENTS
from app.user_data import USERS


API = Api(app)
SWAGGER = Swagger(app)

EVENT_FIELDS = {
    'title': fields.String,
    'location': fields.String,
    'time': fields.String,
    'date': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    # 'uri': fields.Url('event')
}

USER_FIELDS = {
    'email': fields.String,
    'name': fields.String,
    'password': fields.String
}

USER_LOGIN_FIELDS = {
    'email': fields.String,
    'password': fields.String
}

RSVP_FIELDS = {
    'name': fields.String,
    'email': fields.String
}

EMAIL_VALIDATOR = re.compile(r'.+?@.+?\..+')


class EventList(Resource):
    """
    Creates a Eventlist object.
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided')
        self.reqparse.add_argument('location', type=str,)
        self.reqparse.add_argument('time', type=str, required=True)
        self.reqparse.add_argument('date', type=str, required=True)
        self.reqparse.add_argument('description', type=str,)
        super(EventList, self).__init__()


    @staticmethod
    def get():
        """
        Gets Events
        ---
        tags:
          - restful
        responses:
          200:
            description: The event data
        """
        return {'event': [marshal(event, EVENT_FIELDS) for event in EVENTS]}, 200

    def post(self):
        """
        Creates a new event
        ---
        tags:
          - restful
        parameters:
          - in: formData
            name: title
            type: string
            required: true
          - in: formData
            name: location
            type: string
            required: true
          - in: formData
            name: date
            type: string
            required: true
          - in: formData
            name: time
            type: string
            required: true
          - in: formData
            name: description
            type: string
            required: true
        responses:
          201:
            description: The Event has been created
        """
        args = self.reqparse.parse_args()
        event = {
            'id': EVENTS[-1]['id'] + 1,
            'title': args['title'],
            'location': args['location'],
            'time': args['time'],
            'date': args['date'],
            'description': args['description'],
            'done': False,
            'rsvp': []
        }
        EVENTS.append(event)
        return {'event': marshal(event, EVENT_FIELDS)}, 201


class Event(Resource):
    """
    Handle Event crud operation.
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str,
                                   help='No title title provided')
        self.reqparse.add_argument('location', type=str,)
        self.reqparse.add_argument('time', type=str)
        self.reqparse.add_argument('date', type=str)
        self.reqparse.add_argument('description', type=str,)
        super(Event, self).__init__()

    @staticmethod
    def get(eventid):
        """
        Retrieve single event data
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: id
            required: true
            description: The ID of the Event, try 1!
            type: string
        responses:
          200:
            description: The RSVP data
        """
        event = [event for event in EVENTS if event['id'] == eventid]
        if not event:
            abort(404)
        return {'events': marshal(event[0], EVENT_FIELDS)}, 200

    def put(self, eventid):
        """
        Update single event data
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: id
            type: string
            required: true
            description: The ID of the Event must be an interger, try 1!
          - in: formData
            name: title
            type: string
          - in: formData
            name: location
            type: string
          - in: formData
            name: date
            type: string
          - in: formData
            name: time
            type: string
          - in: formData
            name: description
            type: string
        responses:
          201:
            description: The Event has been updated
        """
        event = [event for event in EVENTS if event['id'] == eventid]
        if not event:
            abort(404)
        event = event[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                event[k] = v
        return {'events': marshal(event, EVENT_FIELDS)}, 201

    @staticmethod
    def delete(eventid):
        """
        Delete single event data
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: id
            required: true
            description: The ID of the Event, try 1!
            type: string
        responses:
          204:
            description: The RSVP data
        """
        event = [event for event in EVENTS if event['id'] == eventid]
        if not event:
            abort(404)
        EVENTS.remove(event[0])
        return {'result': True}, 204


class User(Resource):
    """
    Handle User Registration.
    """

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email',
                                   type=str, required=True, help='Please include an email!')
        self.reqparse.add_argument('password',
                                   type=str, required=True, help='Password is required!')
        self.reqparse.add_argument('name',
                                   type=str, required=True, help='Name is Required!')
        super(User, self).__init__()

    @staticmethod
    def get():
        """
        Gets Users
        ---
        tags:
          - restful
        responses:
          200:
            description: The task data
        """
        return {'user': [marshal(user, USER_FIELDS) for user in USERS]}, 200

    def post(self):
        """
        Registers a new user
        ---
        tags:
          - restful
        parameters:
          - in: formData
            name: name
            type: string
            required: true
          - in: formData
            name: email
            type: string
            required: true
          - in: formData
            name: password
            type: string
            required: true
        responses:
          201:
            description: The task has been created
        """
        user_email = [user['email'] for user in USERS]
        args = self.reqparse.parse_args()
        email_match = re.match(EMAIL_VALIDATOR, args['email'])
        if not email_match:
            return 'Wrong email format', 403
        password = args['password']
        if len(password) < 5:
            return 'Password too short, minimum 5 characters', 403
        count = 1
        prev = ''
        for letter in password:
            if letter == ' ':
                return 'Password should not contain spaces', 404
            elif prev == letter:
                count += 1
                if count == 2:
                    return "Too many repetitions of {}".format(letter), 403
            else:
                prev = letter
                count = 0

        user = {
            'id': USERS[-1]['id'] + 1,
            'name': args['name'],
            'email': args['email'],
            'password': args['password']
        }
        if user['email'] not in user_email:
            USERS.append(user)
            return {'user': marshal(user, USER_FIELDS)}, 201
        else:
            return 'Email already exists. Try another Email adress', 403


class UserLogin(Resource):
    """
    Check if user exists then login
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email',
                                   type=str, required=True, help='Email is required!')
        self.reqparse.add_argument('password',
                                   type=str, required=True, help='Password is required!')
        super(UserLogin, self).__init__()

    def post(self):
        """
        User Login
        ---
        tags:
          - restful
        parameters:
          - in: formData
            name: email
            type: string
            required: true
            description: The email of the user, try john.D@gmail.com!
          - in: formData
            name: password
            type: string
            required: true
            description: The password of the user, try qwerty1234!
        responses:
          200:
            description: User has logged in
        """
        args = self.reqparse.parse_args()
        users = {
            'email': args['email'],
            'password': args['password']
        }
        for user in USERS:
            if users['email'] == user['email']:
                if user['password'] == users['password']:
                    return {'users': marshal(users, USER_LOGIN_FIELDS)}, 200
                return 'Wrong password', 401
        return 'Wrong email or email doesn\'t exist', 404


class ResetPassword(Resource):
    """
    Check if user exists then rest password
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email',
                                   type=str, required=True, help='Email is required!')
        self.reqparse.add_argument('password',
                                   type=str, required=True, help='Password is required!')
        super(ResetPassword, self).__init__()


    def post(self):
        """
        Password Reset
        ---
        tags:
          - restful
        parameters:
          - in: formData
            name: email
            type: string
            required: true
            description: Enter the current email of the user, try john.D@gmail.com!
          - in: formData
            name: password
            type: string
            description: Enter the new password of the user!
        responses:
          201:
            description: The Password has been rest
        """
        user_email = [user['email'] for user in USERS]
        args = self.reqparse.parse_args()
        users = {
            'email': args['email'],
            'password': args['password']
        }
        if users['email'] not in user_email:
            return 'Wrong email or Email doesn\'t exist', 404
        else:
            return {'reset': marshal(users, USER_LOGIN_FIELDS)}, 201


class RSVP(Resource):
    """
    Lists all RSVP per event
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('name', type=str,
                                   help='Name is required')
        self.reqparse.add_argument('email', type=str,
                                   help='Name is required')
        super(RSVP, self).__init__()

    def post(self, eventid):
        """
        Retrieve event RSVP
        ---
        tags:
        - restful
        parameters:
        - in: path
            name: id
            required: true
            description: The ID of the Event, try 1!
            type: string
        - in: formData
            name: name
            required: true
            description: The name of the user!
            type: string
        - in: formData
            name: email
            description: The email of the user!
            type: string
        responses:
        200:
            description: The RSVP data
        """
        event = [event for event in EVENTS if event['id'] == eventid]
        if not event:
            abort(404)
        rsvp_list = event[0]['rsvp']
        args = self.reqparse.parse_args()
        rsvp = {
            'user_id': rsvp_list[-1]['user_id'] + 1,
            'name': args['name'],
            'email': args['email']
        }

        for rsvplist in event:
            for rsvpemail in rsvplist['rsvp']:
                if rsvp['email'] == rsvpemail['email']:
                    return 'You have already RSVP to the event', 403
        rsvp_list.append(rsvp)
        return {'rsvp': marshal(rsvp_list, RSVP_FIELDS)}, 201

# events url
API.add_resource(EventList, '/api/events', endpoint='event')
API.add_resource(Event, '/api/events/<int:eventid>', endpoint='events')

# users url
API.add_resource(User, '/api/auth/register', endpoint='user')
API.add_resource(UserLogin, '/api/auth/login', endpoint='users')

# Reset Password
API.add_resource(ResetPassword, '/api/auth/reset-password', endpoint='reset')

# RSVP url
API.add_resource(RSVP, '/api/events/<int:eventid>/rsvp', endpoint='rsvp')
