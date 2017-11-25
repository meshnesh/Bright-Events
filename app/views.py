
    #!/bin/env python
# -*- coding: utf-8 -*-
"""import depancies."""
from flask import Flask, jsonify, abort, make_response, request
from flask_restful import reqparse, abort, Api, Resource
from app import app
# import json

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
    if event_id not in EVENTS:
        abort(404, message="Events {} doesn't exist".format(event_id))

parser = reqparse.RequestParser()
parser.add_argument('title')


class Event(Resource):
    def get(self, event_id):
        abort_if_event_doesnt_exist(event_id)
        return EVENTS[event_id]

    def delete(self, event_id):
        """
        Deletes a single event
        """
        abort_if_event_doesnt_exist(event_id)
        del EVENTS[event_id]
        return '', 204




# Eventlist
# shows a list of all events, and lets you POST to add new tasks

class EventList(Resource):
    """
    Creates a Eventlist object.
    """
    def get(self):
        return EVENTS

    def post(self):
        args = parser.parse_args()
        event_id = int(max(EVENTS.keys()).lstrip('event')) + 1
        event_id = 'event%i' % event_id
        EVENTS[event_id] = {
            'title': args['title'],
            'location':args.get('location'),
            'time':args.get('time', ""),
            'date':args.get('date', ""),
            'description': args.get('description', ""),
            'done': False,
            'rsvp': []

        }
        return EVENTS[event_id], 201

    # def create_event(self):
    #     """Create new event."""
    #     data = request.get_json()
    #     if not data or not 'title' in data:
    #         abort(400)
    #         event = {
    #             'id': events[-1]['id'] + 1,
    #             'title': data['title'],
    #             'location':data.get('location', ""),
    #             'time':data.get('time', ""),
    #             'date':data.get('date', ""),
    #             'description': data.get('description', ""),
    #             'done': False
    #         }
    #     events.append(event)
    #     return jsonify({'event': event}), 201




api.add_resource(EventList, '/events')
api.add_resource(Event, '/events/<event_id>')
