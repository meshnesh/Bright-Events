
import unittest, requests
from flask import json
from app import app
from app.views import EVENTS, Event, EventList, User, UserLogin, PasswordRest, RSVP, abort_if_event_doesnt_exist

class TestEvents(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.event = EventList()
        self.test_client = self.app.test_client
        self.eventCreate = {
            'title':'Orange Harvest',
            'location':'Kitui, Kenya',
            'time':'11:00AM',
            'date': '25 NOV 2017',
            'description':'Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s,'
        }

    def tearDown(self):
        del self.event
        del self.test_client

    def test_get_events(self):
        """Test that gets all events"""
        res = self.event.get()
        self.assertEqual(res, EVENTS)

    def test_add_event(self):
        """Test that adds all events"""
        resp = self.test_client().post('/api/events', data=self.eventCreate)
        self.assertEqual(resp.status_code, 201)

    def test_get_single_event(self):
        """Test that gets single event"""
        resp = self.test_client().get('/api/events/event1')
        self.assertEqual(resp.status_code, 200)

    def test_delete_event(self):
        """Test that event gets delete"""
        resp = self.test_client().delete('/api/events/event2')
        self.assertEqual(resp.status_code, 204)

    def test_put_event(self):
        """Test that event get put"""
        resp = self.test_client().put('/api/events/event1', data=self.eventCreate)
        self.assertEqual(resp.status_code, 201)
     





















# class TestEvents(unittest.TestCase):
#     def setUp(self):
#         self.req = app.test_client()
#         self.events = EVENTS

#     def tearDown(self):
#         self.events.clear()
#         self.events = None

#     def get_events(self):
#       return self.req.get('/api/events')

#     def add_event(self, data={}):
#       return self.req.post('/api/events', 
#         data=json.dumps(data), 
#         content_type='application/json'
#         )

#     def test_initial_events(self):
#         r = self.get_events()
#         self.assertEqual(r.status_code, 200, 'Status Code not 200')
#         body = json.loads(r.data)
#         print(("imported events", self.events))
#         print(("response events", body.get('events', [])))
#         self.assertEqual(self.events, body.get('events', []), 'Events array not equal')

#     def test_add_event(self):
#         event = {
#             "title": "YO",
#             "location": 'NRB'
#         }
#         r = self.add_event(event)
#         self.assertEqual(r.status_code, 201, 'Status Code not 201')
#         body = json.loads(r.data)
#         self.assertTrue(set(event.items()).issubset(set(body['event'].items())))




if __name__ == "__main__":
    unittest.main()