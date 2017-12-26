# -*- coding: utf-8 -*-
"""import depancies."""
import unittest
from app import app


class TestUsers(unittest.TestCase):
    """Test user registration and login"""
    def setUp(self):
        self.app = app
        self.test_client = self.app.test_client
        self.createuser = {
            'name': u'Tonnie Nesh',
            'email': u'tonnie.nesh@gmail.com',
            'password': u'qwerty1'
        }
        self.checkuser = {
            'name': u'John Doe',
            'email': u'john.D@gmail.com',
            'password': u'qwerty1234'
        }
        self.checkemail = {
            'name': u'John Doe',
            'email': u'john.Dgmail.com',
            'password': u'qwerty1234'
        }
        self.checkcredentials = {
            'name': u'John Doe',
            'password': u'qwerty1234'
        }
        self.check_login_credentials = {
            'email': u'alex@gmail.com',
            'password': u'qwerty1234'
        }
        self.checkpassword = {
            'email': u'john.D@gmail.com',
            'password': u'qwerty123'
        }

    def tearDown(self):
        del self.test_client
        del self. createuser
        del self.checkuser
        del self.checkemail

    def test_registration(self):
        """Test user Registration"""
        resp = self.test_client().post('/api/auth/register', data=self.createuser)
        self.assertEqual(resp.status_code, 201)

    def test_duplicate_email(self):
        """Test if user email Exists in registration"""
        resp = self.test_client().post('/api/auth/register', data=self.checkuser)
        self.assertEqual(resp.status_code, 403)

    def test_email_format(self):
        """Test user email is the correct format in registration"""
        resp = self.test_client().post('/api/auth/register', data=self.checkemail)
        self.assertEqual(resp.status_code, 403)

    def test_required_credentials(self):
        """Test user in registration provides all credentials"""
        resp = self.test_client().post('/api/auth/register', data=self.checkcredentials)
        self.assertEqual(resp.status_code, 400)

    def test_user_login(self):
        """Test user login"""
        resp = self.test_client().post('/api/auth/login', data=self.createuser)
        self.assertEqual(resp.status_code, 200)

    def test_user_login_credentials(self):
        """Test user login with unregistered email"""
        resp = self.test_client().post('/api/auth/login', data=self.check_login_credentials)
        self.assertEqual(resp.status_code, 404)

    def test_user_login_password(self):
        """Test user login password if correct"""
        resp = self.test_client().post('/api/auth/login', data=self.checkpassword)
        self.assertEqual(resp.status_code, 401)


class TestResetPassword(unittest.TestCase):
    """Test password reset"""
    def setUp(self):
        self.app = app
        self.test_client = self.app.test_client
        self.resetpassword = {
            'email': u'john.D@gmail.com',
            'password': u'qwerty1234'
        }
        self.checkemail = {
            'email': u'alex@gmail.com',
            'password': u'qwerty123'
        }

    def tearDown(self):
        del self.test_client
        del self.resetpassword
        del self.checkemail

    def test_email_exists(self):
        """Test email exists before password rest"""
        resp = self.test_client().post('/api/auth/reset-password', data=self.checkemail)
        self.assertEqual(resp.status_code, 404)

    def test_password_reset(self):
        """Test password rest"""
        resp = self.test_client().post('/api/auth/reset-password', data=self.resetpassword)
        self.assertEqual(resp.status_code, 201)

if __name__ == "__main__":
    unittest.main()
