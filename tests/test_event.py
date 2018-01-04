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

    def test_event_creation(self):
        """Test API can create an event (POST request)"""
        res = self.client().post('/api/events/', data=self.event)
        self.assertEqual(res.status_code, 201)
        self.assertIn('Vacation', str(res.data))

    def test_api_can_get_all_events(self):
        """Test API can get events (GET request)."""
        res = self.client().post('/api/events/', data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().get('/api/events/')
        self.assertEqual(res.status_code, 200)
        self.assertIn('Vacation', str(res.data))

    def test_api_can_get_event_by_id(self):
        """Test API can get a single event by using it's id."""
        res = self.client().post('/api/events/', data=self.event)
        self.assertEqual(res.status_code, 201)
        result_in_json = json.loads(res.data.decode('utf-8').replace("'", "\""))
        result = self.client().get(
            '/api/events/{}'.format(result_in_json['id']))
        self.assertEqual(result.status_code, 200)
        self.assertIn('Vacation', str(result.data))

    def test_event_can_be_edited(self):
        """Test API can edit an existing event. (PUT request)"""
        res = self.client().post(
            '/api/events/',
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().put(
            '/api/events/1',
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
        results = self.client().get('/api/events/1')
        self.assertIn('Climbing Mt Kenya', str(results.data))

    def test_event_deletion(self):
        """Test API can delete an existing event. (DELETE request)."""
        res = self.client().post(
            '/api/events/',
            data=self.event)
        self.assertEqual(res.status_code, 201)
        res = self.client().delete('/api/events/1')
        self.assertEqual(res.status_code, 200)
        # Test to see if it exists, should return a 404
        result = self.client().get('/api/events/1')
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
