#!/bin/env python
# -*- coding: utf-8 -*-
"""import depancies."""
import re
from flask import abort
from flask_restful import reqparse, Api, Resource, fields, marshal
from flasgger import Swagger
from app import app

from app.data import EVENTS
from app.user_data import USERS


api = Api(app)
swagger = Swagger(app)

event_fields = {
    'title': fields.String,
    'location': fields.String,
    'time': fields.String,
    'date': fields.String,
    'description': fields.String,
    'done': fields.Boolean,
    # 'uri': fields.Url('event')
}

user_fields = {
    'email': fields.String,
    'name': fields.String,
    'password': fields.String
}

user_login_fields = {
    'email': fields.String,
    'password': fields.String
}

rsvp_fields = {
    'name': fields.String,
    'email': fields.String
}

email_validator = re.compile(r'.+?@.+?\..+')

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
        return {'event': [marshal(event, event_fields) for event in EVENTS]}, 200

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
        return {'event': marshal(event, event_fields)}, 201

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
    def get(id):
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
        event = [event for event in EVENTS if event['id'] == id]
        if len(event) == 0:
            abort(404)
        return {'events': marshal(event[0], event_fields)}, 200

    def put(self, id):
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
        event = [event for event in EVENTS if event['id'] == id]
        if len(event) == 0:
            abort(404)
        event = event[0]
        args = self.reqparse.parse_args()
        for k, v in args.items():
            if v is not None:
                event[k] = v
        return {'events': marshal(event, event_fields)}, 201

    @staticmethod
    def delete(id):
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
        event = [event for event in EVENTS if event['id'] == id]
        if len(event) == 0:
            abort(404)
        EVENTS.remove(event[0])
        return {'result': True}, 204

# End of Eventlist
# shows a list of all events, and lets you POST to add new tasks

# User registration
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
        return {'user': [marshal(user, user_fields) for user in USERS]}, 200

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
        userEmail = [user['email'] for user in USERS]
        args = self.reqparse.parse_args()
        email_match = re.match(email_validator, args['email'])
        if not email_match:
            return 'Wrong email format', 404
        password = args['password']
        if len(password) < 5:
            return 'Password too short', 404
        count = 1
        prev = ''
        for letter in password:
            if letter == ' ':
                return 'No spaces you fool', 404
            elif prev == letter:
                count += 1
                if count == 2:
                    return "Too many repetitions of {}".format(letter), 404
            else:
                prev = letter
                count = 0

        user = {
            'id': USERS[-1]['id'] + 1,
            'name': args['name'],
            'email': args['email'],
            'password': args['password']
        }
        if user['email'] not in userEmail:
            USERS.append(user)
            return {'user': marshal(user, user_fields)}, 201
        else:
            return 'Email already exists. Try another Email adress', 404

# User login
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
                    return {'users': marshal(users, user_login_fields)}, 200
                return 'Wrong password', 405
        return 'Wrong email or email doesn\'t exist', 404

# User reset password
class PasswordRest(Resource):
    """
    Check if user exists then login
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email',
                                   type=str, required=True, help='Email is required!')
        self.reqparse.add_argument('password',
                                   type=str, required=True, help='Password is required!')
        super(PasswordRest, self).__init__()


    def post(self):
        """
        Paasword Reset
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
        userEmail = [user['email'] for user in USERS]
        args = self.reqparse.parse_args()
        users = {
            'email': args['email'],
            'password': args['password']
        }
        if users['email'] not in userEmail:
            return 'Wrong email or Email doesn\'t exist', 404
        else:
            return {'reset': marshal(users, user_login_fields)}, 201

# RSVP
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

    @classmethod
    def get(cls, id):
        """
        Retrieve event RSVP
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: id
            required: true
            description: The ID of the Event, try event1!
            type: string
        responses:
          200:
            description: The RSVP data
        """
        event = [event for event in EVENTS if event['id'] == id]
        if len(event) == 0:
            abort(404)
        rsvpList = event[0]['rsvp']
        return {'rsvp': marshal(rsvpList, rsvp_fields)}, 200

    def post(self, id):
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
          event = [event for event in EVENTS if event['id'] == id]
          if len(event) == 0:
                abort(404)
          rsvpList = event[0]['rsvp']
          print(rsvpList)
          args = self.reqparse.parse_args()
          rsvp = {
            'user_id': rsvpList[-1]['user_id'] + 1,
            'name': args['name'],
            'email': args['email']
          }
          rsvpList.append(rsvp)
          return {'rsvp': marshal(rsvpList, rsvp_fields)}, 201

# events url
api.add_resource(EventList, '/api/events', endpoint='event')
api.add_resource(Event, '/api/events/<int:id>', endpoint='events')

# users url
api.add_resource(User, '/api/auth/register', endpoint='user')
api.add_resource(UserLogin, '/api/auth/login', endpoint='users')

# Reset Password
api.add_resource(PasswordRest, '/api/auth/reset-password', endpoint='reset')

# RSVP url
api.add_resource(RSVP, '/api/events/<int:id>/rsvp', endpoint='rsvp')
