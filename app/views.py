#!/bin/env python
# -*- coding: utf-8 -*-
"""import depancies."""
from flask import Flask, jsonify, abort, make_response, request
from flask_restful import reqparse, abort, Api, Resource
from app import app

from app import data

api = Api(app)

EVENTS = {
    'event1': {
        'title': u'Mango Harvest',
        'location': u'Kitui, Kenya',
        'time': u'11:00AM',
        'date': u'25 NOV 2017',
        'description': u'Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s,',
        'done': False,
        'rsvp': [
            {
                'user_id': 1,
                'name': u'John Doe',
                'email': u'john.D@gmail.com'
            },
            {
                'user_id': 3,
                'name': u'Antony Ng\'ang\'a',
                'email': u'tonny.nesh@gmail.com'
            }
        ]
    },
    'event2':{
        'title': u'Python Meetup',
        'location':u'Nairobi, Kenya',
        'time':u'07:00PM',
        'date':u'30 NOV 2017',
        'description': u'Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s,',
        'done': False,
        'rsvp': [
            {
                'user_id': 2,
                'name': u'Mary Jane',
                'email': u'jane.mary@yahoo.com'
            }
        ]
    }
}


USERS = {
    'user1': {
        'name': u'John Doe',
        'email': u'john.D@gmail.com',
        'password': u'qwerty1234'
    },
    'user2': {
        'user_id': 2,
        'name': u'Mary Jane',
        'email': u'jane.mary@yahoo.com',
        'password': u'qwerty1234'
    },
    'user3': {
        'user_id': 3,
        'name': u'Antony Ng\'ang\'a',
        'email': u'tonny.nesh@gmail.com',
        'password': u'qwerty1234'
    }
}

def abort_if_event_doesnt_exist(event_id):
    """
    Handle Error when Event not found.
    """
    if event_id not in EVENTS:
        abort(404, message="Events {} doesn't exist".format(event_id))

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
        Retrieve Event
        """
        abort_if_event_doesnt_exist(event_id)
        return EVENTS[event_id]

    def delete(self, event_id):
        """
        Delete a single event
        """
        abort_if_event_doesnt_exist(event_id)
        del EVENTS[event_id]
        return '', 204

    def put(self, event_id):
        """
        Edit a single event
        """
        args = self.reqparse.parse_args()
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
        List all Events
        """
        return EVENTS

    def post(self):
        """
        Creates a new Event.
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
    """
    User Registration and login.
    """
    def __init__(self):
        self.reqparse = reqparse.RequestParser()
        self.reqparse.add_argument('email', type=str, required=True, help='Password is required!')
        self.reqparse.add_argument('password', type=str, required=True, help='Please include an email!')
        self.reqparse.add_argument('name', type=str, required=True, help='Name is Required!')
        super(User, self).__init__()

    def get(self):
        """
        List all Users
        """
        return USERS

    def post(self):
        """
        User Registration.
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
# RSVP
class RSVP(Resource):
    """
    Lists all RSVP per event
    """
    def get(self, event_id):
        """
        Retrieve rsvp
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

# RSVP url
api.add_resource(RSVP, '/api/events/<event_id>/rsvp')