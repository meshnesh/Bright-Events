"""import depancies and methods."""

import re
from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User, BlacklistToken
from flask_bcrypt import Bcrypt

from . import auth_blueprint

EMAIL_VALIDATOR = re.compile(r'.+?@.+?\..+')


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
                user = User(name=name, email=email, password=password)
                email_match = re.match(EMAIL_VALIDATOR, user.email)

                if not email_match:
                    response = {
                        'message': 'Wrong email format. Check your Email.'
                    }
                    return make_response(jsonify(response)), 403

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
            else:
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

        # Query to see if the user email exists
        user = User.query.filter_by(email=request.data['email']).first()
        if user:
            access_token = user.generate_token(user.id)
            if access_token:
                response = {
                    'message': 'Email confirmed you can reset your password.',
                    'access_token': access_token.decode()
                }
                return make_response(jsonify(response)), 200

        response = {
            'message': 'Wrong Email or user email does not exist.'
        }
        return make_response(jsonify(response)), 401


class RestPasswordView(MethodView):
    """This class resets a users password. Url ---> /api/auth/reset-password"""

    @staticmethod
    def put():
        """This Handles PUT request for handling the reset password for the user
        ---> /api/auth/reset-password
        """

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                try:
                    reset_password = User.query.filter_by(id=user_id).first_or_404()

                    post_data = request.data
                    name = reset_password.name
                    email = reset_password.email
                    reset_password.password = Bcrypt().generate_password_hash(
                        post_data['password']).decode()
                    user = User(name=name, email=email, password=reset_password.password)
                    user.reset_password()

                    response = {
                        'message': 'Password rest successfully. Please log in.'
                    }
                    # return a response notifying the user that password was reset successfully
                    return make_response(jsonify(response)), 201
                except Exception as error:
                    # An error occured, therefore return a string message containing the error
                    response = {
                        'message': str(error)
                    }
                    return make_response(jsonify(response)), 401
        message = user_id
        response = {
            'message': message
        }
        return make_response(jsonify(response)), 401


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
            if not isinstance(resp, str):
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
                    return make_response(response_object), 401

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


# Define the API resource
REGISTRATION_VIEW = RegistrationView.as_view('REGISTRATION_VIEW')
LOGIN_VIEW = LoginView.as_view('LOGIN_VIEW')
RESET_VIEW = RestEmailView.as_view('RESET_VIEW')
RESET_PASSWORD_VIEW = RestPasswordView.as_view('RESET_PASSWORD_VIEW')
USER_VIEW = UserAPI.as_view('USER_VIEW')
LOGOUT_VIEW = LogoutAPI.as_view('LOGOUT_VIEW')


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

# Define the rule for the rest_password url --->  /api/auth/rest-password
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/reset-password',
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
