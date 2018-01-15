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
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    db.init_app(app)


    @app.route('/api/events/', methods=['POST', 'GET'])
    def event():
        # """Function to handle POST and GET requests for events."""
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

    @app.route('/api/events/all', methods=['GET'])
    def get_event():
        """Function to handle GET requests and filter for events."""
        # GET all the events for this user
        events = Events.query
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        args = {}
        potential_search = ['title', 'location', 'cartegory']

        for search_res in potential_search:
            var = request.args.get(search_res)
            if var:
                args.update({search_res:var})

        if args:
            events = Events.query.filter_by(**args)

        eventPage = events.paginate(page, limit, False).items

        results = []

        for event in eventPage:
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

        if not results:
            response = {
                'message': "No events found"
            }
            return make_response(jsonify(response)), 404

        return make_response(jsonify(results)), 200

    @app.route('/api/events/<int:event_id>', methods=['GET', 'PUT', 'DELETE'])
    def event_manipulation(event_id):
        """Handles the manupilation of event data, with GET, PUT and DELETE by event id."""

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # retrieve an event using it's ID
                event = Events.query.filter_by(id=event_id).first_or_404()

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
                    response = {
                        'id': event.id,
                        'title': event.title,
                        'location': event.location,
                        'time': event.time,
                        'date': event.date,
                        'description': event.description,
                        'cartegory':event.cartegory,
                        'imageUrl':event.imageUrl,
                        'created_by': event.created_by
                    }
                    return make_response(jsonify(response)), 200
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
                        'imageUrl':event.imageUrl,
                        'created_by': event.created_by
                    })
                    return make_response(response), 200
            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401


    @app.route('/api/events/<int:event_id>/rsvp/', methods=['POST'])
    def create_rsvp(event_id):
        """Adds a user to rsvp to a specific event."""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                event = Events.query.filter_by(id=event_id).first_or_404()

                # POST User to the RSVP
                user = User.query.filter_by(id=user_id).first_or_404()
                has_prev_rsvpd = event.add_rsvp(user)
                if has_prev_rsvpd:
                    response = {
                        'message': 'You have already reserved a seat'
                    }
                    return make_response(jsonify(response)), 202

                response = {
                    'message': 'You have Reserved a seat'
                }
                return make_response(jsonify(response)), 200

            else:
                # user is not legit, so the payload is an error message
                message = user_id
                response = {
                    'message': message
                }
                return make_response(jsonify(response)), 401


    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    return app
