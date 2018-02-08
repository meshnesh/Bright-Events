"""import depancies."""

import unittest
import os
import json
from itsdangerous import URLSafeTimedSerializer
from app import create_app, db

SECRET = URLSafeTimedSerializer(os.getenv('SECRET'))

class AuthTestCase(unittest.TestCase):
    """Test case for the authentication blueprint."""

    def setUp(self):
        """Set up test variables."""
        self.app = create_app(config_name="testing")
        # initialize the test client
        self.client = self.app.test_client

        with self.app.app_context():
            # create all tables
            db.session.close()
            db.drop_all()
            db.create_all()

    def user_registration(self):
        """This helper method helps register a test user."""
        user_data = {
            'name':'test user',
            'email': 'test@example.com',
            'password': 'test_password'
        }
        return self.client().post('/api/auth/register', data=user_data)

    def user_login(self):
        """This helper method helps log in a test user."""
        user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        return self.client().post('/api/auth/login', data=user_data)

    def get_access_token(self):
        """register and login a user to get an access token"""
        self.user_registration()
        result = self.user_login()
        access_token = json.loads(result.data.decode())['access_token']
        return access_token

    def user_email_reset(self):
        """This helper method helps check user email to reset password."""
        user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        return self.client().post('/api/auth/reset', data=user_data)

    def user_email_confirm(self):
        """This helper method helps check user email to confirm it."""
        user_data = {
            'email': 'test@example.com',
            'password': 'test_password'
        }
        return self.client().post('/api/auth/confirm', data=user_data)

    def email_verification(self):
        """This helper send an Email checking if valid and verify it through token"""
        new_data={
            "email_confirmed" : True
        }

        self.user_registration()
        self.user_email_confirm()

        token1 = SECRET.dumps('test@example.com', salt='email-confirm')

        return self.client().put('/api/auth/verify/'+token1, data=new_data)

    def user_logout(self):
        """This helper method helps log out a test user."""
        access_token = self.get_access_token()

        response = self.client().post(
            '/api/auth/logout',
            headers=dict(
                Authorization='Bearer ' + access_token)
        )

        return response

    def test_registration(self):
        """Test user registration works correcty."""
        register_user = self.user_registration()
        self.assertEqual(register_user.status_code, 201)

        result = json.loads(register_user.data.decode())
        self.assertEqual(
            result['message'], "You registered successfully. Please log in.")

    def test_already_registered_user(self):
        """Test that a user cannot be registered twice."""
        self.user_registration() # register a user
        second_res = self.user_registration() # re-register the same user
        self.assertEqual(second_res.status_code, 202)
        # get the results returned in json format
        result = json.loads(second_res.data.decode())
        self.assertEqual(
            result['message'], "User already exists. Please login.")

    def test_user_login(self):
        """Test registered user can login."""
        self.user_registration()
        login_user = self.user_login()
        self.assertEqual(login_user.status_code, 200)

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
        self.user_registration()
        res = self.user_email_reset()

        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], "Check your email to reset your password.")
        self.assertEqual(res.status_code, 200)

    def test_email_non_exist_for_reset(self):
        """Test not registered Email fails when reseting there password"""
        self.user_registration() # register a user

        not_a_user = {
            'email': 'not_a_user@example.com'
        }

        reset_res = self.client().post(
            '/api/auth/reset', data=not_a_user
        ) # make request with a none existence user

        result = json.loads(reset_res.data.decode())
        self.assertEqual(result['message'], "Wrong Email or user email does not exist.")
        self.assertEqual(reset_res.status_code, 401)

    def test_user_status(self):
        """ Test for user status """
        access_token = self.get_access_token()

        response = self.client().get(
            '/api/auth/status',
            headers=dict(
                Authorization='Bearer ' + access_token)
        )
        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['data'] is not None)
        self.assertEqual(response.status_code, 200)

    def test_valid_logout(self):
        """ Test for logout before token expires """
        response = self.user_logout()

        data = json.loads(response.data.decode())
        self.assertTrue(data['status'] == 'success')
        self.assertTrue(data['message'] == 'Successfully logged out.')
        self.assertEqual(response.status_code, 200)

    def test_invalid_logout(self):
        """ Test for logout after already logged out  """
        self.user_logout() # valid token logout
        second_login = self.user_logout() # secondary logout

        self.assertEqual(second_login.status_code, 401)

    def test_email_exist_for_confirmation(self):
        """Test Email is valid by sending an email and  being confirmed """
        self.user_registration()
        res = self.user_email_confirm()

        result = json.loads(res.data.decode())
        self.assertEqual(result['message'], "Check your Email to Verify it.")
        self.assertEqual(res.status_code, 200)

    def test_email_verification(self):
        """Test Email is valid by sending url token and verify it """
        response = self.email_verification()

        data = json.loads(response.data.decode())
        self.assertTrue(data['message'] == 'Email Confirmed successfully. You can enjoy the app features.')
        self.assertEqual(response.status_code, 201)

    def tearDown(self):
        """teardown all initialized variables."""
        with self.app.app_context():
            # drop all tables
            db.session.remove()
            db.drop_all()

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
