# test_bucketlist.py
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
            'title': 'Vacation',
            'location':'JKIA',
            'time':'12:00PM',
            'date':'20th DEC 2017',
            'description':'Going to Borabora for vacation and chill',
            'imageUrl':'https://www.google.com',
            'cartegory':'Lifestyle'
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.create_all()

    def register_user(self, name="test user", email="user@test.com", password="test1234"):
        """This helper method helps register a test user."""
        user_data = {
            'name':name,
            'email': email,
            'password': password
        }
        return self.client().post('/auth/register', data=user_data)

    def login_user(self, email="user@test.com", password="test1234"):
        """This helper method helps log in a test user."""
        user_data = {
            'email': email,
            'password': password
        }
        return self.client().post('/auth/login', data=user_data)

    def test_event_creation(self):
        """Test API can create an event (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Vacation', str(res.data))

    def test_api_can_get_all_events(self):
        """Test API can get events (GET request)."""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)

        res = self.client().get(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 200)
        self.assertIn('Vacation', str(res.data))

    def test_api_can_get_event_by_id(self):
        """Test API can get a single event by using it's id."""
         # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)

        results = json.loads(res.data.decode())
        result = self.client().get(
            '/api/eventlist/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Vacation', str(result.data))

    def test_event_can_be_edited(self):
        """Test API can edit an existing event. (PUT request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        # get the json with the event
        results = json.loads(res.data.decode())

        res = self.client().put(
            '/api/events/{}'.format(results['id']),
            data={
                'title': 'Climbing Mt Kenya',
                'location':'Nyeri',
                'time':'12:00PM',
                'date':'20th DEC 2017',
                'description':'Climb the Mountain',
                'imageUrl':'https://www.google.com',
                'cartegory':'Lifestyle'
            })
        self.assertEqual(res.status_code, 200)

        results = self.client().get(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Climbing Mt Kenya', str(results.data))

    def test_event_deletion(self):
        """Test API can delete an existing event. (DELETE request)."""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events/',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        # get the json with the event
        results = json.loads(res.data.decode())

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

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable

if __name__ == "__main__":
    unittest.main()
