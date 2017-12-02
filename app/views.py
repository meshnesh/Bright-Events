#!/bin/env python
# -*- coding: utf-8 -*-
"""import depancies."""
from flask import abort,request
from flask_restful import reqparse, Api, Resource
from flasgger import Swagger, swag_from
from app import app


from app.data import EVENTS
from app.user_data import USERS

api = Api(app)
swagger = Swagger(app)

def abort_if_event_doesnt_exist(event_id):
    """
    Handle Error when Event not found.
    """
    if event_id not in EVENTS:
        abort(404, message="Events {} doesn't exist".format(event_id))

def abort_if_user_doesnt_exist(user_id):
    """
    Handle Error when User not found.
    """
    if user_id not in USERS:
        abort(404, message="Invalid User {} doesn't exist".format(user_id))

class Event(Resource):
    """
    Handle Event crud operation.
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('title', type=str, required=True,
                                   help='No task title provided')
        self.reqparse.add_argument('location', type=str,)
        self.reqparse.add_argument('time', type=str, required=True)
        self.reqparse.add_argument('date', type=str, required=True)
        self.reqparse.add_argument('description', type=str,)
        super(Event, self).__init__()

    def get(self, event_id):
        """
        Retrieve single event data
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: Event_id
            required: true
            description: The ID of the Event, try event1!
            type: string
        responses:
          200:
            description: The RSVP data
        """
        abort_if_event_doesnt_exist(event_id)
        return EVENTS[event_id]

    def delete(self, event_id):
        """
        Delete single event data
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: Event_id
            required: true
            description: The ID of the Event, try event1!
            type: string
        responses:
          204:
            description: The RSVP data
        """
        abort_if_event_doesnt_exist(event_id)
        del EVENTS[event_id]
        return 'Event deleted', 204

    def put(self, event_id):
        """
        This is an example
        ---
        tags:
          - restful
        parameters:
          - in: formData
            name: event_id
            type: string
            required: true
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
            description: The Event has been updated
        """
        args = self.reqparse.parse_args()
        EVENTS[event_id] = {
            'title': args['title'],
            'location': args['location'],
            'time': args.get('time',""),
            'date': args['date'],
            'description': args['description'],
            'done': False,
            'rsvp': []
        }
        return EVENTS[event_id], 201

# Eventlist
# shows a list of all events, and lets you POST to add new tasks

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


    def get(self):
        """
        Gets Events
        ---
        tags:
          - restful
        responses:
          200:
            description: The event data
        """
        return EVENTS

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
        event_id = int(max(EVENTS.keys()).lstrip('event')) + 1
        event_id = 'event%i' % event_id
        EVENTS[event_id] = {
            'title': args['title'],
            'location': args['location'],
            'time': args['time'],
            'date': args['date'],
            'description': args['description'],
            'done': False,
            'rsvp': []
        }
        return EVENTS[event_id], 201

# User registration
class User(Resource):
    # @swag_from('colors.yml', methods=['POST','GET'])

    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, help='Please include an email!')
        self.reqparse.add_argument('password', type=str, required=True, help='Password is required!')
        self.reqparse.add_argument('name', type=str, required=True, help='Name is Required!')
        super(User, self).__init__()

    def get(self):
        """
        Gets Users
        ---
        tags:
          - restful
        responses:
          200:
            description: The task data
            schema:
              id: Tasks
              properties:
                task_id:
                  type: object
                  schema:
                    $ref: '#/definitions/Task'
        """
        return USERS

    # swag_from('colors.yml')
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
            schema:
              $ref: '#/definitions/Task'
          - in: formData
            name: email
            type: string
            required: true
            schema:
              $ref: '#/definitions/Task'
          - in: formData
            name: password
            type: string
            required: true
            schema:
              $ref: '#/definitions/Task'
        responses:
          201:
            description: The task has been created
            schema:
              $ref: '#/definitions/Task'
        """
        args = self.reqparse.parse_args()
        user_id = int(max(USERS.keys()).lstrip('user')) + 1
        user_id = 'user%i' % user_id
        USERS[user_id] = {
            'email': args['email'],
            'password': args['password'],
            'name': args['name'],
        }
        return USERS[user_id], 201

# User login
class UserLogin(Resource):
    """
    Check if user exists then login
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, help='Email is required!')
        self.reqparse.add_argument('password', type=str, required=True, help='Password is required!')
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
          - in: formData
            name: password
            type: string
            required: true
        responses:
          200:
            description: User has logged in
        """
        args = self.reqparse.parse_args()
        USERS = {
            'email': args['email'],
            'password': args['password']
        }
        return USERS, 200

# User reset password
class PasswordRest(Resource):
    """
    Check if user exists then login
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('password', type=str, required=True, help='Password is required!')
        super(PasswordRest, self).__init__()


    def put(self):
        """
        Paasword Reset
        ---
        tags:
          - restful
        parameters:
          - in: formData
            name: password
            required: true
            description: The ID of the task, try 42!
            type: string
        responses:
          201:
            description: The task has been updated
        """
        args = self.reqparse.parse_args()
        user_id = int(max(USERS.keys()).lstrip('user')) + 1
        user_id = 'user%i' % user_id
        USERS[user_id] = {
            'email': args.get('email', "tonny.nesh@gmail.com"),
            'password': args['password'],
            'name': args.get('name', "Antony Ng'ang'a"),
        }
        return USERS[user_id], 201


# RSVP
class RSVP(Resource):
    """
    Lists all RSVP per event
    """
    def get(self, event_id):
        """
        Retrieve event RSVP
        ---
        tags:
          - restful
        parameters:
          - in: path
            name: Event_id
            required: true
            description: The ID of the Event, try event1!
            type: string
        responses:
          200:
            description: The RSVP data
        """
        abort_if_event_doesnt_exist(event_id)
        event = EVENTS[event_id]
        rsvpList = event['rsvp']
        return rsvpList


# events url
api.add_resource(EventList, '/api/events')
api.add_resource(Event, '/api/events/<event_id>')

# users url
api.add_resource(User, '/api/auth/register')
api.add_resource(UserLogin, '/api/auth/login')

# RSVP url
api.add_resource(RSVP, '/api/events/<event_id>/rsvp')

# Reset Password
api.add_resource(PasswordRest, '/api/auth/reset-password')
