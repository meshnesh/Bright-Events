# test_event.py
import unittest
import os
import json
from app import create_app, db

class EventTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.event = {
            "cartegory": "Lifestyle",
            "date": "6th JAN 2017",
            "description": "Swim for the first time in a lake",
            "id": 7,
            "imageUrl": "https://www.google.com",
            "location": "Naivasha",
            "time": "10:00AM",
            "title": "Swimming In Lake Turkana"
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self, name="test user", email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'name':name,
            'email': email,
            'password': password
        }
        return self.client().post('/api/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/api/auth/login', data=user_data)

    def test_event_creation(self):
        """Test API can create an event (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Swimming In Lake Turkana', str(res.data))

    def test_api_can_get_all_user_events(self):
        """Test API can get an event (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Swimming In Lake Turkana', str(res.data))

    def test_api_can_get_user__single_event(self):
        """Test API can get a single event by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())
        result = self.client().get(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Swimming In Lake Turkana', str(result.data))

    def test_events_can_be_edited(self):
        """Test API can edit an existing event. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(rv.status_code, 201)
        # get the json with the event
        results = json.loads(rv.data.decode())
        rv = self.client().put(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token),
            data={
                "cartegory": "Lifestyle",
                "date": "6th JAN 2017",
                "description": "Swim for the first time in a lake",
                "id": 5,
                "imageUrl": "https://www.google.com",
                "location": "Naivasha",
                "time": "10:00AM",
                "title": "Swimming In Lake Naivasha"
            })

        self.assertEqual(rv.status_code, 200)
        results = self.client().get(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Swimming In Lake Naivasha', str(results.data))

    def test_event_deletion(self):
        """Test API can delete an existing event. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']


        rv = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data={'title': 'Swimming'})
        self.assertEqual(rv.status_code, 201)
        # get the json with the event
        results = json.loads(rv.data.decode())

        res = self.client().delete(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token)
            )
        self.assertEqual(res.status_code, 200)

        # Test to see if it exists, should return a 404
        result = self.client().get(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token)
            )
        self.assertEqual(result.status_code, 404)

    def test_user_rsvp(self):
        """Test API User can RSVP to an existing event. (POST request)."""
        #register the user and login
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        #let's create an event
        rv = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(rv.status_code, 201)
        # get the json with the event
        results = json.loads(rv.data.decode())

        # lets rsvp to the event now
        rv = self.client().post(
            '/api/events/{}/rsvp/'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)


    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
