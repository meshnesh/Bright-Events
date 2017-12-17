#!/bin/env python
# -*- coding: utf-8 -*-
"""import depancies."""
import unittest
from app import app
from app.views import EventList, User, PasswordRest, RSVP

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
        del self.eventCreate

    def test_get_events(self):
        """Test that gets all events"""
        res = self.test_client().get('/api/events')
        self.assertEqual(res.status_code, 200)

    def test_add_event(self):
        """Test that adds all events"""
        resp = self.test_client().post('/api/events', data=self.eventCreate)
        self.assertEqual(resp.status_code, 201)

    def test_get_single_event(self):
        """Test that gets single event"""
        resp = self.test_client().get('/api/events/1')
        self.assertEqual(resp.status_code, 200)

    def test_delete_event(self):
        """Test that event gets delete"""
        resp = self.test_client().delete('/api/events/2')
        self.assertEqual(resp.status_code, 204)

    def test_put_event(self):
        """Test that event get put"""
        resp = self.test_client().put('/api/events/1', data=self.eventCreate)
        self.assertEqual(resp.status_code, 201)

class TestRSVP(unittest.TestCase):
    """Test event rsvp"""
    def setUp(self):
        self.app = app
        self.rsvp = RSVP()
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
        del self.rsvp
        del self.test_client
        del self.testrsvp
        del self.testemailexist

    def test_event_rsvp(self):
        """Test user event rsvp"""
        res = self.test_client().post('/api/events/1/rsvp', data=self.testrsvp)
        self.assertEqual(res.status_code, 201)

    def test_email_exist(self):
        """Test user event rsvp"""
        res = self.test_client().post('/api/events/1/rsvp', data=self.testemailexist)
        self.assertEqual(res.status_code, 403)


class TestUsers(unittest.TestCase):
    """Test user registration and login"""
    def setUp(self):
        self.app = app
        self.user = User()
        self.test_client = self.app.test_client
        self.createuser = {
            'name': u'Tonnie Nesh',
            'email': u'tonnie.nesh@gmail.com',
            'password': u'qwerty1'
        }
        self.checkuser = {
            'name': u'Mary Jane',
            'email': u'john.D@gmail.com',
            'password': u'qwerty1234'
        }

    def tearDown(self):
        del self.user
        del self.test_client
        del self. createuser
        del self.checkuser

    def test_user_reg_email_exist(self):
        """Test user Registration"""
        resp = self.test_client().post('/api/auth/register', data=self.checkuser)
        self.assertEqual(resp.status_code, 404)

    def test_reg_email_not_exist(self):
        """Test user Registration"""
        resp = self.test_client().post('/api/auth/register', data=self.createuser)
        self.assertEqual(resp.status_code, 201)

    def test_user_login(self):
        """Test user login"""
        resp = self.test_client().post('/api/auth/login', data=self.checkuser)
        self.assertEqual(resp.status_code, 200)

class TestResetPassword(unittest.TestCase):
    """Test password reset"""
    def setUp(self):
        self.app = app
        self.passwordrest = PasswordRest()
        self.test_client = self.app.test_client
        self.resetpassword = {
            'name': u'Mary Jane',
            'email': u'john.D@gmail.com',
            'password': u'qwerty1234'
        }

    def tearDown(self):
        del self.passwordrest
        del self.test_client
        del self.resetpassword

    def test_password_reset(self):
        """Test password rest"""
        resp = self.test_client().post('/api/auth/reset-password', data=self.resetpassword)
        self.assertEqual(resp.status_code, 201)

if __name__ == "__main__":
    unittest.main()
