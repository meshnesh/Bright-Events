from . import auth_blueprint

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User


class RegistrationView(MethodView):
    """This class registers a new user."""

    def post(self):
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

    def post(self):
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
    """This class resets a users password."""

    def post(self):
        """Handle PUT request for this view. Url ---> /auth/register"""

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



# Define the API resource
registration_view = RegistrationView.as_view('registration_view')
login_view = LoginView.as_view('login_view')
reset_view = RestEmailView.as_view('rest_view')


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

# Define the rule for the rest(to validate the email) url --->  /auth/rest
# Then add the rule to the blueprint
auth_blueprint.add_url_rule(
    '/api/auth/reset',
    view_func=reset_view,
    methods=['POST']
)
