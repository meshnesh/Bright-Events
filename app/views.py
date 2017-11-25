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
        # self.reqparse.add_argument('location', type=str,)
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
        title = {'title': args['title']}
        EVENTS[event_id] = title
        return title, 201


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
        # args = self.parser.parse_args()
        event_id = int(max(EVENTS.keys()).lstrip('event')) + 1
        event_id = 'event%i' % event_id
        EVENTS[event_id] = {
            'title': args['title'],
            'location': args['location'],
            'time':args.get('time', ""),
            'date':args.get('date', ""),
            'description': args.get('description', ""),
            'done': False,
            'rsvp': []
        }
        return EVENTS[event_id], 201


# Eventlist
# shows a list of all events, and lets you POST to add new tasks


api.add_resource(EventList, '/events')
api.add_resource(Event, '/events/<event_id>')
