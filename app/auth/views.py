"""import depancies and methods."""

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User, BlacklistToken
from flask_bcrypt import Bcrypt

from . import auth_blueprint


class RegistrationView(MethodView):
    """This class registers a new user."""

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
    """This class-based view handles user login and access token generation."""

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
    """This class validates a user email then generates a token to reset a users password."""

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
    """This class resets a users password."""

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
    User Resource
    """
    def get(self):
        # get the auth token
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            resp = User.decode_token(access_token)
            if not isinstance(resp, str):
                user = User.query.filter_by(id=resp).first()
                responseObject = {
                    'status': 'success',
                    'data': {
                        'user_id': user.id,
                        'email': user.email
                    }
                }
                return make_response(jsonify(responseObject)), 200
            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401

        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 401


class LogoutAPI(MethodView):
    """
    Logout Resource
    """
    def post(self):
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
                    responseObject = jsonify({
                        'status': 'success',
                        'message': 'Successfully logged out.'
                    })
                    return make_response(responseObject), 200
                except Exception as error:
                    responseObject = jsonify({
                        'status': 'fail',
                        'message': error
                    })
                    return make_response(responseObject), 200

            responseObject = {
                'status': 'fail',
                'message': resp
            }
            return make_response(jsonify(responseObject)), 401

        responseObject = {
            'status': 'fail',
            'message': 'Provide a valid auth token.'
        }
        return make_response(jsonify(responseObject)), 403


# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
reset_view = RestEmailView.as_view('rest_view')
reset_password_view = RestPasswordView.as_view('rest_password_view')
user_view = UserAPI.as_view('user_api')
logout_view = LogoutAPI.as_view('logout_api')


# Define the rule for the registration url --->  /api/auth/register
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/register',
    view_func=registration_view,
    methods=['POST'])

# Define the rule for the registration url --->  /api/auth/login
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/login',
    view_func=login_view,
    methods=['POST']
)

# Define the rule for the rest(to validate the email) url --->  /api/auth/rest
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/reset',
    view_func=reset_view,
    methods=['POST']
)

# Define the rule for the rest_password url --->  /api/auth/rest-password
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/reset-password',
    view_func=reset_password_view,
    methods=['PUT']
)

auth_blueprint.add_url_rule(
    '/auth/status',
    view_func=user_view,
    methods=['GET']
)

auth_blueprint.add_url_rule(
    '/auth/logout',
    view_func=logout_view,
    methods=['POST']
)