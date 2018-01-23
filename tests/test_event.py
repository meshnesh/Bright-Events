"""import depancies and methods."""

import unittest
import json
from app import create_app, db

class EventTestCase(unittest.TestCase):
    """This class represents the bucketlist test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client
        self.event = {
            "category": "Lifestyle",
            "date": "6th JAN 2017",
            "description": "Swim for the first time in a lake",
            "id": 7,
            "image_url": "https://www.google.com",
            "location": "Naivasha",
            "time": "10:00AM",
            "title": "swimming in lake turkana"
        }

        # binds the app to the current context
        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def register_user(self):
        """This helper method helps register a test user."""
        user_data = {
            'name':'test user',
            'email': 'user@test.com',
            'password': 'test1234'
        }
        return self.client().post('/api/auth/register', data=user_data)

    def login_user(self):
        """This helper method helps log in a test user."""
        user_data = {
            'email': 'user@test.com',
            'password': 'test1234'
        }
        return self.client().post('/api/auth/login', data=user_data)

    def test_api_get_all_events(self):
        """Test API can get all events without token passed (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Swimming in lake turkana', str(res.data))

    def test_api_get_single_event(self):
        """Test API can get a single event by using it's id. with out valid token"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())
        result = self.client().get(
            '/api/events/all/{}'.format(results['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Swimming in lake turkana', str(result.data))

    def test_event_creation(self):
        """Test API can create an event (POST request)"""
        # register a test user, then log them in
        self.register_user()
        result = self.login_user()
        # obtain the access token
        access_token = json.loads(result.data.decode())['access_token']

        # ensure the request has an authorization header set with the access token in it
        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Swimming in lake turkana', str(res.data))

    def test_api_get_all_user_events(self):
        """Test API can get all events with token passed (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Swimming in lake turkana', str(res.data))

    def test_api_get_user_single_event(self):
        """Test API can get a single event by using it's id."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(rv.status_code, 201)
        results = json.loads(rv.data.decode())
        result = self.client().get(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Swimming in lake turkana', str(result.data))

    def test_events_can_be_edited(self):
        """Test API can edit an existing event. (PUT request)"""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        rv = self.client().post(
            '/api/events',
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
                "image_url": "https://www.google.com",
                "location": "Naivasha",
                "time": "10:00AM",
                "title": "Swimming in lake naivasha"
            })

        self.assertEqual(rv.status_code, 200)
        results = self.client().get(
            '/api/events/{}'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertIn('Swimming in lake naivasha', str(results.data))

    def test_event_deletion(self):
        """Test API can delete an existing event. (DELETE request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']


        rv = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
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
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(rv.status_code, 201)
        # get the json with the event
        results = json.loads(rv.data.decode())

        # lets rsvp to the event now
        rv = self.client().post(
            '/api/events/{}/rsvp'.format(results['id']),
            headers=dict(Authorization="Bearer " + access_token))
        self.assertEqual(result.status_code, 200)

    def test_api_can_filter_event_title(self):
        """Test API can filter an event by title (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?title=Swimming in lake turkana'
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Swimming in lake turkana', str(res.data))

    def test_filter_not_event_title(self):
        """Test API can filter an event by title non existence (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?title=vacation'
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn('No events found', str(res.data))

    def test_filter_event_location(self):
        """Test API can filter an event by location (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?location=Naivasha'
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Naivasha', str(res.data))

    def test_filter_none_event_location(self):
        """Test API can filter an event by location which does not exist (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?location=Nairobi'
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn('No events found', str(res.data))

    def test_filter_event_category(self):
        """Test API can filter an event by category (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?category=Lifestyle'
        )
        self.assertEqual(res.status_code, 200)
        self.assertIn('Lifestyle', str(res.data))

    def test_filter_not_event_category(self):
        """Test API can filter an event by category that does not exist (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?category=Education'
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn('No events found', str(res.data))

    def test_filter_event_all_search(self):
        """Test API can filter an event by category, location, title (GET request)."""
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?title=Swimming in lake turkana&location=Naivasha&category=Lifestyle'
        )
        # self.assertEqual(res.status_code, 200)
        self.assertIn('Lifestyle', str(res.data))

    def test_event_filter_no_title(self):
        """Test API can filter an event by category, location, title
        with wrong title (GET request).
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?title=Hiking Mt Kenya&location=Naivasha&category=Lifestyle'
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn('No events found', str(res.data))

    def test_event_wrong_location(self):
        """Test API can filter an event by category, location, title
        with wrong location (GET request).
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?title=Swimming In Lake Turkana&location=Turkana&category=Lifestyle'
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn('No events found', str(res.data))

    def test_event_wrong_category(self):
        """Test API can filter an event by category, location, title
        with wrong category (GET request).
        """
        self.register_user()
        result = self.login_user()
        access_token = json.loads(result.data.decode())['access_token']

        res = self.client().post(
            '/api/events',
            headers=dict(Authorization="Bearer " + access_token),
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get(
            '/api/events/all?title=Swimming In Lake Turkana&location=Naivasha&category=Education'
        )
        self.assertEqual(res.status_code, 404)
        self.assertIn('No events found', str(res.data))

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
