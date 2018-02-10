"""import depancies and methods."""
import os
import re
from flask.views import MethodView
from flask import make_response, request, jsonify, render_template, url_for
from app.models import User, BlacklistToken
from flask_bcrypt import Bcrypt
from itsdangerous import URLSafeTimedSerializer, SignatureExpired
from app.emails import send_mail, confirm_token

from . import auth_blueprint

EMAIL_VALIDATOR = re.compile(r'.+?@.+?\..+')
SECRET = URLSafeTimedSerializer(os.getenv('SECRET'))


class RegistrationView(MethodView):
    """This class registers a new user. Url ---> /api/auth/register"""

    @staticmethod
    def post():
        """Handle POST request for this view. Url ---> /api/auth/register"""
        # Query to see if the user already exists
        user = User.query.filter_by(email=request.data['email']).first()

        if not user:
            # There is no user so we'll try to register them
            try:
                post_data = request.data
                # Register the user
                name = post_data['name']
                email = post_data['email']
                password = post_data['password']
                email_confirmed = False

                user = User(
                    name=name, email=email, password=password,
                    email_confirmed=email_confirmed
                )

                email_match = re.match(EMAIL_VALIDATOR, user.email)

                if not email_match:
                    response = {
                        'message': 'Wrong email format. Check your Email.'
                    }
                    return make_response(jsonify(response)), 403
                count = 1
                prev = ''
                for letter in password:
                    if letter == ' ':
                        response = {
                            'message':'Password should not contain spaces'
                        }
                        return make_response(jsonify(response)), 403
                    elif prev == letter:
                        count += 1
                        if count == 2:
                            response = {
                                'message':'Too many repetitions of {}'.format(letter)
                            }
                            return make_response(jsonify(response)), 403
                    else:
                        prev = letter
                        count = 0

                token = SECRET.dumps(user.email, salt='email-confirm')
                subject = "welcome to Bright Events"

                link = url_for("auth.VERIFY_VIEW", token=token, _external=True)
                html = render_template("inline_welcome.html", name=name, link=link)

                send_mail(to=user.email, subject=subject, html=html)

                user.save()

                response = {
                    'message': 'You registered successfully. Please log in.'
                }
                # return a response notifying the user that they registered successfully
                return make_response(jsonify(response)), 201
            except Exception as error:
                # An error occured, therefore return a string message containing the error
                response = {
                    'message': str(error)
                }
                return make_response(jsonify(response)), 401
        else:
            # There is an existing user. We don't want to register users twice
            # Return a message to the user telling them that they they already exist
            response = {
                'message': 'User already exists. Please login.'
            }

            return make_response(jsonify(response)), 202


class LoginView(MethodView):
    """This class handles user login and
    access token generation. Url ---> /api/auth/login"""

    @staticmethod
    def post():
        """Handle POST request for this view. Url ---> /api/auth/login"""
        try:
            # Get the user object using their email (unique to every user)
            user = User.query.filter_by(email=request.data['email']).first()
            # Authenticate the found user using their password
            if user and user.password_is_valid(request.data['password']):
                # Generate the access token. This will be used as the authorization header
                access_token = user.generate_token(user.id)
                if access_token:
                    response = {
                        'message': 'You logged in successfully.',
                        'access_token': access_token.decode()
                    }
                    return make_response(jsonify(response)), 200
            # User does not exist. Therefore, we return an error message
            response = {
                'message': 'Invalid email or password, Please try again'
            }
            return make_response(jsonify(response)), 401

        except Exception as error:
            # Create a response containing an string error message
            response = {
                'message': str(error)
            }
            # Return a server error using the HTTP Error Code 500 (Internal Server Error)
            return make_response(jsonify(response)), 500


class RestEmailView(MethodView):
    """This class validates a user email then
    generates a token to reset a users password. Url ---> /api/auth/reset"""

    @staticmethod
    def post():
        """Handle POST request for this view. Url ---> /api/auth/reset"""
        user = User.query.filter_by(email=request.data['email']).first()
        if user:
            token = SECRET.dumps(user.email, salt='reset-password')
            subject = "Reset Password"

            link = url_for("auth.RESET_PASSWORD_VIEW", token=token, _external=True)
            html = render_template("inline_reset.html", link=link)

            send_mail(to=user.email, subject=subject, html=html)

            response = {
                'message': 'Check your email to reset your password.'
            }
            return make_response(jsonify(response)), 200

        response = {
            'message': 'Wrong Email or user email does not exist.'
        }
        return make_response(jsonify(response)), 401


class RestPasswordView(MethodView):
    """This class resets a users password. Url ---> /api/auth/reset-password/<token>"""

    @staticmethod
    @confirm_token('reset-password')
    def put(token, email):
        """This Handles PUT request for handling the reset password for the user
        ---> /api/auth/reset-password/<token>
        """

        reset_password = User.query.filter_by(email=email).first()

        post_data = request.data
        reset_password.password = Bcrypt().generate_password_hash(
            post_data['password']).decode()
        reset_password.update_user_data()


        response = {
            'message': 'Password rest successfully. Please log in.'
        }
        # return a response notifying the user that password was reset successfully
        return make_response(jsonify(response)), 201


class UserAPI(MethodView):
    """
    Class handles getting User Resource of a valid user token. Url ---> /api/auth/status
    """

    @staticmethod
    def get():
        """Get the email and id of a user"""

        # get the auth token
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            resp = User.decode_token(access_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                response_object = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email
                    }
                }
                return make_response(jsonify(response_object)), 200
            response_object = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(response_object)), 401

        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(response_object)), 401


class LogoutAPI(MethodView):
    """
    Handles logging out of a user from the application. Url ---> /api/auth/logout
    """

    @staticmethod
    def post():
        """Makes a post request of the user valid token and black lists it if still valid"""

        # get auth token
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            resp = User.decode_token(access_token)
            if isinstance(resp, int):
                # mark the token as blacklisted
                blacklist_token = BlacklistToken(token=access_token)
                try:
                    blacklist_token.save()
                    response_object = jsonify({
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    })
                    return make_response(response_object), 200
                except Exception as error:
                    response_object = jsonify({
                        'status': 'fail',
                        'message': error
                    })
                    return make_response(response_object), 200

            response_object = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(response_object)), 401

        response_object = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(response_object)), 403


class ConfirmEmailView(MethodView):
    """This class validates a user email then
    generates a token to reset a users password. Url ---> /api/auth/confirm"""

    @staticmethod
    def post():
        """Handle POST request for this view. Url ---> /api/auth/confirm"""
        user = User.query.filter_by(email=request.data['email']).first()
        name = user.name
        if user:
            if user.email_confirmed is True: # checking if email mail already confirmed
                response = {
                    'message': 'Email already Confirmed.'
                }
                return make_response(jsonify(response)), 401

            token = SECRET.dumps(user.email, salt='email-confirm') # create a token with the user email 
            subject = "Email Confirmation" # subject of the email

            link = url_for("auth.VERIFY_VIEW", token=token, _external=True)
            html = render_template("inline_confirm.html", name=name, link=link)

            send_mail(to=user.email, subject=subject, html=html) # send the email to the user

            response = {
                'message': 'Check your Email to Verify it.'
            }
            return make_response(jsonify(response)), 200

        response = {
            'message': 'Wrong Email or user email does not exist.'
        }
        return make_response(jsonify(response)), 401


class VerifyEmailView(MethodView):
    """This class resets a users password. Url ---> /api/auth/verify/<token>"""

    @staticmethod
    @confirm_token('email-confirm')
    def get(token, email):
        """This Handles PUT request for handling the reset password for the user
        ---> /api/auth/verify/<token>
        """

        reset_password = User.query.filter_by(email=email).first()

        reset_password.email_confirmed = True
        reset_password.update_user_data()

        response = {
            'message': 'Email Confirmed successfully. You can enjoy the app features.'
        }
        # return a response notifying the user that password was reset successfully
        return make_response(jsonify(response)), 201


# Define the API resource
REGISTRATION_VIEW = RegistrationView.as_view('REGISTRATION_VIEW')
LOGIN_VIEW = LoginView.as_view('LOGIN_VIEW')
RESET_VIEW = RestEmailView.as_view('RESET_VIEW')
RESET_PASSWORD_VIEW = RestPasswordView.as_view('RESET_PASSWORD_VIEW')
USER_VIEW = UserAPI.as_view('USER_VIEW')
LOGOUT_VIEW = LogoutAPI.as_view('LOGOUT_VIEW')
CONFIRM_VIEW = ConfirmEmailView.as_view('CONFIRM_VIEW')
VERIFY_VIEW = VerifyEmailView.as_view('VERIFY_VIEW')


# Define the rule for the registration url --->  /api/auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/register',
    view_func=REGISTRATION_VIEW,
    methods=['POST'])

# Define the rule for the registration url --->  /api/auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/login',
    view_func=LOGIN_VIEW,
    methods=['POST']
)

# Define the rule for the rest(to validate the email) url --->  /api/auth/rest
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/reset',
    view_func=RESET_VIEW,
    methods=['POST']
)

# Define the rule for the rest_password url --->  /api/auth/rest-password/<token>
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/reset-password/<token>',
    view_func=RESET_PASSWORD_VIEW,
    methods=['PUT']
)

# Define the rule for the rest_password url --->  /api/auth/status
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/status',
    view_func=USER_VIEW,
    methods=['GET']
)

# Define the rule for the rest_password url --->  /api/auth/logout
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/logout',
    view_func=LOGOUT_VIEW,
    methods=['POST']
)

# Define the rule for the rest(to validate the email) url --->  /api/auth/confirm
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/confirm',
    view_func=CONFIRM_VIEW,
    methods=['POST']
)

# Define the rule for the rest_password url --->  /api/auth/verify/<token>
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/verify/<token>',
    view_func=VERIFY_VIEW,
    methods=['GET']
)
