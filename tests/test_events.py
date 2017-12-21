# -*- coding: utf-8 -*-
"""import depancies."""
import unittest
from app import app
from app.views import EventList


class TestEvents(unittest.TestCase):
    """Test event crud functions"""
    def setUp(self):
        self.app = app
        self.event = EventList()
        self.test_client = self.app.test_client
        self.eventcreate = {
            'title':'Orange Harvest',
            'location':'Kitui, Kenya',
            'time':'11:00AM',
            'date': '25 NOV 2017',
            'description':'Lorem Ipsum has been the industry\'s standard dummy text ever since the 1500s,'
        }

    def tearDown(self):
        del self.event
        del self.test_client
        del self.eventcreate

    def test_retrieve_events(self):
        """Test API can retrieve events (GET request)."""
        resp = self.test_client().post('/api/events', data=self.eventcreate)
        self.assertEqual(resp.status_code, 201)
        resp = self.test_client().get('/api/events')
        self.assertIn('Orange Harvest', str(resp.data))

    def test_add_event(self):
        """Test API can create an event"""
        resp = self.test_client().post('/api/events', data=self.eventcreate)
        self.assertEqual(resp.status_code, 201)

    def test_get_single_event(self):
        """Test API can get single event"""
        resp = self.test_client().get('/api/events/1')
        self.assertEqual(resp.status_code, 200)

    def test_put_event(self):
        """Test API can edit single event"""
        resp = self.test_client().put('/api/events/1', data=self.eventcreate)
        self.assertEqual(resp.status_code, 201)

    def test_delete_event(self):
        """Test API can delete single event"""
        resp = self.test_client().delete('/api/events/2')
        resp = self.test_client().get('/api/events/2')
        self.assertEqual(resp.status_code, 404)

    def test_event_not_exists(self):
        """Test API if single event does not exist"""
        resp = self.test_client().get('/api/events/5')
        self.assertEqual(resp.status_code, 404)


class TestRSVP(unittest.TestCase):
    """Test event rsvp"""
    def setUp(self):
        self.app = app
        self.test_client = self.app.test_client
        self.testrsvp = {
            'name': u'John Doe',
            'email': u'atony.nesh@gmail.com'
        }
        self.testemailexist = {
            'name': u'John Doe',
            'email': u'john.D@gmail.com'
        }

    def tearDown(self):
        del self.test_client
        del self.testrsvp
        del self.testemailexist

    def test_event_rsvp(self):
        """Test user can rsvp to an event"""
        res = self.test_client().post('/api/events/1/rsvp', data=self.testrsvp)
        self.assertEqual(res.status_code, 201)

    def test_email_exist(self):
        """Test user email already exist in event rsvp"""
        res = self.test_client().post('/api/events/1/rsvp', data=self.testemailexist)
        self.assertEqual(res.status_code, 403)

if __name__ == "__main__":
    unittest.main()
