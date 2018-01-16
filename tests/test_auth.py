"""import depancies."""

import unittest
import json
from app import create_app, db
from app.models import BlacklistToken

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        # initialize the test client
        self.client = self.app.test_client
        # This is the user test json data with a predefined email and password
        self.user_data = {
            'name':'test user',
            'email': 'test@example.com',
            'password': 'test_password'
        }

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def test_registration(self):
        """Test user registration works correcty."""
        res = self.client().post('/api/auth/register', data=self.user_data)
        # get the results returned in json format
        result = json.loads(res.data.decode())
        # assert that the request contains a success message and a 201 status code
        self.assertEqual(result['message'], "You registered successfully. Please log in.")
        self.assertEqual(res.status_code, 201)

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        res = self.client().post('/api/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        second_res = self.client().post('/api/auth/register', data=self.user_data)
        self.assertEqual(second_res.status_code, 202)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        res = self.client().post('/api/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/auth/login', data=self.user_data)
        result = json.loads(login_res.data.decode())
        self.assertEqual(result['message'], "You logged in successfully.")
        self.assertEqual(login_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_non_registered_user_login(self):
        """Test non registered users cannot login."""
        # define a dictionary to represent an unregistered user
        not_a_user = {
            'email': 'not_a_user@example.com',
            'password': 'nope'
        }
        # send a POST request to /auth/login with the data above
        res = self.client().post('/api/auth/login', data=not_a_user)
        # get the result in json
        result = json.loads(res.data.decode())

        # assert that this response must contain an error message
        # and an error status code 401(Unauthorized)
        self.assertEqual(res.status_code, 401)
        self.assertEqual(
            result['message'], "Invalid email or password, Please try again")

    def test_email_exist_for_reset(self):
        """Test Email exists so that they can reset there password"""
        # send a POST request to /auth/register
        res = self.client().post('/api/auth/register', data=self.user_data)
        # get the result in json
        result = json.loads(res.data.decode())
        # assert that the request contains a 201 status code
        self.assertEqual(res.status_code, 201)

        reset_res = self.client().post('/api/auth/reset', data=self.user_data)
        result = json.loads(reset_res.data.decode())
        self.assertEqual(result['message'], "Email confirmed you can reset your password.")
        self.assertEqual(reset_res.status_code, 200)
        self.assertTrue(result['access_token'])

    def test_email_non_exist_for_reset(self):
        """Test Email exists so that they can reset there password"""
        not_a_user = {
            'email': 'not_a_user@example.com'
        }
        # send a POST request to /auth/register
        res = self.client().post('/api/auth/register', data=self.user_data)
        # get the result in json
        result = json.loads(res.data.decode())
        # assert that the request contains a 201 status code
        self.assertEqual(res.status_code, 201)

        reset_res = self.client().post('/api/auth/reset', data=not_a_user)
        result = json.loads(reset_res.data.decode())
        self.assertEqual(result['message'], "Wrong Email or user email does not exist.")
        self.assertEqual(reset_res.status_code, 401)

    def test_user_reset_password(self):
        """Test Email exists so that they can reset there password"""
        new_password = {
            'password': 'nope'
        }
        # send a POST request to /auth/register
        res = self.client().post('/api/auth/register', data=self.user_data)
        # get the result in json
        result = json.loads(res.data.decode())
        # assert that the request contains a 201 status code
        self.assertEqual(res.status_code, 201)

        reset_res = self.client().post('/api/auth/reset', data=self.user_data)
        result = json.loads(reset_res.data.decode())
        self.assertEqual(result['message'], "Email confirmed you can reset your password.")
        self.assertEqual(reset_res.status_code, 200)
        self.assertTrue(result['access_token'])

        # obtain the access token
        access_token = json.loads(reset_res.data.decode())['access_token']

        password_res = self.client().put(
            '/api/auth/reset-password',
            headers=dict(Authorization="Bearer " + access_token),
            data=new_password)
        self.assertEqual(password_res.status_code, 201)

    def test_user_status(self):
        """ Test for user status """
        res = self.client().post('/api/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/auth/login', data=self.user_data)

        # obtain the access token
        access_token = json.loads(login_res.data.decode())['access_token']

        response = self.client().get(
            '/auth/status',
            headers=dict(
                Authorization='Bearer ' + access_token)
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['data'] is not None)
        self.assertEqual(response.status_code, 200)

    def test_valid_logout(self):
        """ Test for logout before token expires """
        res = self.client().post('/api/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/auth/login', data=self.user_data)

        # get the token
        access_token = json.loads(login_res.data.decode())['access_token']

        # valid token logout
        response = self.client().post(
            '/auth/logout',
            headers=dict(
                Authorization='Bearer ' + access_token)
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully logged out.')
        self.assertEqual(response.status_code, 200)

    def test_valid_blacklisted_token_logout(self):
        """ Test for logout before token expires """
        res = self.client().post('/api/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/auth/login', data=self.user_data)

        # get the token
        access_token = json.loads(login_res.data.decode())['access_token']

        blacklist_token = BlacklistToken(access_token)
        blacklist_token.save()

       # blacklisted valid token logout
        response = self.client().post(
            '/auth/logout',
            headers=dict(
                Authorization='Bearer ' + access_token)
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
        self.assertEqual(response.status_code, 401)

    def test_valid_blacklisted_token_user(self):
        """ Test for user status with a blacklisted valid token """
        res = self.client().post('/api/auth/register', data=self.user_data)
        self.assertEqual(res.status_code, 201)
        login_res = self.client().post('/api/auth/login', data=self.user_data)

         # obtain the access token
        access_token = json.loads(login_res.data.decode())['access_token']

        # blacklist a valid token
        blacklist_token = BlacklistToken(access_token)
        blacklist_token.save()

        response = self.client().get(
            '/auth/status',
            headers=dict(
                Authorization='Bearer ' + access_token)
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'fail')
        self.assertTrue(data['message'] == 'Token blacklisted. Please log in again.')
        self.assertEqual(response.status_code, 401)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()
