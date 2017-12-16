
import unittest
from app import app
from app.views import Event, EventList, User, UserLogin, PasswordRest, RSVP

# class TestRSVP(unittest.TestCase):
#     """Test event rsvp"""
#     def setUp(self):
#         self.app = app
#         self.rsvp = RSVP()
#         self.test_client = self.app.test_client
#         self.testRsvp = {
#             'name': u'John Doe',
#             'email': u'john.D@gmail.com'
#         }

#     def tearDown(self):
#         del self.rsvp
#         del self.test_client
#         del self.testRsvp

#     def test_event_rsvp(self):
#         """Test user event rsvp"""
#         res = self.test_client().post('/api/events/2/rsvp', data=self.testRsvp)
#         self.assertEqual(res.status_code, 201)

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

class TestUsers(unittest.TestCase):
    """Test user registration and login"""
    def setUp(self):
        self.app = app
        self.user = User()
        self.test_client = self.app.test_client
        self.createUser = {
            'name': u'Tonnie Nesh',
            'email': u'tonnie.nesh@gmail.com',
            'password': u'qwerty1'
        }
        self.checkUser = {
            'name': u'Mary Jane',
            'email': u'john.D@gmail.com',
            'password': u'qwerty1234'
        }

    def tearDown(self):
        del self.user
        del self.test_client
        del self. createUser
        del self.checkUser

    def test_user_registration_email_exists(self):
        """Test user Registration"""
        resp = self.test_client().post('/api/auth/register', data=self.checkUser)
        self.assertEqual(resp.status_code, 404)

    def test_registration_emailNot_exist(self):
        """Test user Registration"""
        resp = self.test_client().post('/api/auth/register', data=self.createUser)
        self.assertEqual(resp.status_code, 201)

    def test_user_login(self):
        """Test user login"""
        resp = self.test_client().post('/api/auth/login', data=self.checkUser)
        self.assertEqual(resp.status_code, 200)

class TestResetPassword(unittest.TestCase):
    """Test password reset"""
    def setUp(self):
        self.app = app
        self.passwordRest = PasswordRest()
        self.test_client = self.app.test_client
        self.resetPassword = {
            'name': u'Mary Jane',
            'email': u'john.D@gmail.com',
            'password': u'qwerty1234'
        }

    def tearDown(self):
        del self.passwordRest
        del self.test_client
        del self.resetPassword

    def test_password_reset(self):
        """Test password rest"""
        resp = self.test_client().post('/api/auth/reset-password', data=self.resetPassword)
        self.assertEqual(resp.status_code, 201)

if __name__ == "__main__":
    unittest.main()
