# app/__init__.py
import json
from flask_api import FlaskAPI, status
from flask_sqlalchemy import SQLAlchemy

from flask import request, jsonify, abort, make_response

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    """Creates a new Flask object and returns when it's configured
    and connected with the db."""

    from app.models import Events, User

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/events/', methods=['POST', 'GET'])
    def event():
        """Function to handle POST and GET requests for events."""
        # get the access token
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # Go ahead and handle the request, the user is authed
                if request.method == "POST":
                    title = str(request.data.get('title', ''))
                    location = str(request.data.get('location', ''))
                    time = str(request.data.get('time', ''))
                    date = str(request.data.get('date', ''))
                    description = str(request.data.get('description', ''))
                    cartegory = str(request.data.get('cartegory', ''))
                    imageUrl = str(request.data.get('imageUrl', ''))
                    if title:
                        event = Events(
                            title=title,
                            location=location,
                            time=time, date=date,
                            description=description,
                            cartegory=cartegory,
                            imageUrl=imageUrl,
                            created_by=user_id)
                        event.save()
                        response = jsonify({
                            'id': event.id,
                            'title': event.title,
                            'location': event.location,
                            'time': event.time,
                            'date': event.date,
                            'description': event.description,
                            'cartegory':event.cartegory,
                            'imageUrl':event.imageUrl,
                            'created_by': user_id
                        })

                        return make_response(response), 201

                else:
                    # GET
                    # get all the events for this user
                    events = Events.get_all_user(user_id)
                    results = []

                    for event in events:
                        obj = {
                            'id': event.id,
                            'title': event.title,
                            'location': event.location,
                            'time': event.time,
                            'date': event.date,
                            'description': event.description,
                            'cartegory':event.cartegory,
                            'imageUrl':event.imageUrl
                        }
                        results.append(obj)

                    return make_response(jsonify(results)), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401

    @app.route('/api/events/<int:id>', methods=['GET', 'PUT', 'DELETE'])
    def event_manipulation(id, **kwargs):
        """Handles the manupilation of event data, with GET, PUT and DELETE by event id."""
     # retrieve a buckelist using it's ID
        event = Events.query.filter_by(id=id).first_or_404()

        if request.method == 'DELETE':
            event.delete()
            return {
                "message": "event {} deleted successfully".format(event.id)
            }, 200

        elif request.method == 'PUT':
            title = str(request.data.get('title', ''))
            location = str(request.data.get('location', ''))
            time = str(request.data.get('time', ''))
            date = str(request.data.get('date', ''))
            description = str(request.data.get('description', ''))
            cartegory = str(request.data.get('cartegory', ''))
            imageUrl = str(request.data.get('imageUrl', ''))

            event.title = title
            event.location = location
            event.time = time
            event.date = date
            event.description = description
            event.cartegory = cartegory
            event.imageUrl = imageUrl

            event.save()
            response = jsonify({
                'id': event.id,
                'title': event.title,
                'location': event.location,
                'time': event.time,
                'date': event.date,
                'description': event.description,
                'cartegory':event.cartegory,
                'imageUrl':event.imageUrl
            })
            response.status_code = 200
            return response
        else:
            # GET
            response = jsonify({
                'id': event.id,
                'title': event.title,
                'location': event.location,
                'time': event.time,
                'date': event.date,
                'description': event.description,
                'cartegory':event.cartegory,
                'imageUrl':event.imageUrl
            })
            response.status_code = 200
            return response

    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)
    
    return app
