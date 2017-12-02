
import unittest, requests
from flask import json
from app import app
from app.views import EVENTS, Event, EventList, User, UserLogin, PasswordRest, RSVP, abort_if_event_doesnt_exist

class TestEvents(unittest.TestCase):
    """Test event crud functions"""
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

class TestUsers(unittest.TestCase):
    """Test user registration and login"""
    def setUp(self):
        self.app = app
        self.user = User()
        self.test_client = self.app.test_client
        self.createUser = {
            'name': u'Mary Jane',
            'email': u'jane.mary@yahoo.com',
            'password': u'1234qwerty'
        }

    def tearDown(self):
        del self.user
        del self.test_client

    def test_user_registration(self):
        """Test user Registration"""
        resp = self.test_client().post('/api/auth/register', data=self.createUser)
        self.assertEqual(resp.status_code, 201)

    def test_user_login(self):
        """Test user login"""
        resp = self.test_client().post('/api/auth/login', data=self.createUser)
        self.assertEqual(resp.status_code, 200)

class TestResetPassword(unittest.TestCase):
    """Test password reset"""
    def setUp(self):
        self.app = app
        self.passwordRest = PasswordRest()
        self.test_client = self.app.test_client
        self.resetPassword = {
            'name': u'Mary Jane',
            'email': u'jane.mary@yahoo.com',
            'password': u'qwerty1234'
        }

    def tearDown(self):
        del self.passwordRest
        del self.test_client

    def test_password_reset(self):
        """Test password rest"""
        resp = self.test_client().put('/api/auth/reset-password', data=self.resetPassword)
        self.assertEqual(resp.status_code, 201)


class TestRSVP(unittest.TestCase):
    """Test password reset"""
    def setUp(self):
        self.app = app
        self.rsvp = RSVP()
        self.test_client = self.app.test_client

    def tearDown(self):
        del self.rsvp
        del self.test_client

    def test_user_login(self):
        """Test user login"""
        resp = self.test_client().get('/api/events/event1/rsvp')
        self.assertEqual(resp.status_code, 200)


if __name__ == "__main__":
    unittest.main()
