"""import depancies and methods."""

from flask.views import MethodView
from flask import make_response, request, jsonify
from flask_mail import Mail, Message
from app.models import User, Events, EventCategory, BlacklistToken
from app import create_app

from run import CONFIG_NAME

from . import events_blueprint

APP = create_app(CONFIG_NAME)
MAIL = Mail(APP)


class AllEventsView(MethodView):
    """This class gets all events with out token validation."""

    @staticmethod
    def get():
        """Handle POST request for this view. Url ---> /api/events/all"""

        # GET all the events for this user
        events = Events.query
        categories = EventCategory.get__all_categories()
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)

        args = {}
        potential_search = ['event_category']

        for search_res in potential_search:
            var = request.args.get(search_res)
            if var:
                args.update({search_res:var})

        arr = ['title', 'location']
        categ = request.args.get('event_category')
        if categ:
            events = events.filter_by(event_category=categ)
        for element in arr:
            val = request.args.get(element)
            if val:
                events = events.filter(getattr(Events, element).ilike('%{}%'.format(val)))

        event_page = events.paginate(page, limit, False).items

        results = []

        for event in event_page:
            obj = {
                'id': event.id,
                'title': event.title,
                'location': event.location,
                'time': event.time,
                'date': event.date,
                'description': event.description,
                'image_url':event.image_url,
                'event_category':event.event_category
            }
            results.append(obj)

        if not results:
            response = {
                'message': "No events found"
            }
            return make_response(jsonify(response)), 404

        return make_response(jsonify(results)), 200


class SingleEventView(MethodView):
    """This class handles getting single event
    with out token validation. Url ---> /api/events/all/<int:event_id>"""

    @staticmethod
    def get(event_id):
        """Handle getting a single event by id"""
        event = Events.query.filter_by(id=event_id).first_or_404()
        categories = EventCategory.get__all_categories()
        for category in categories:
            event.event_category = category.category_name
        response = jsonify({
            'id': event.id,
            'title': event.title,
            'location': event.location,
            'time': event.time,
            'date': event.date,
            'description': event.description,
            'image_url':event.image_url,
            'created_by': event.created_by,
            'event_category':event.event_category
        })
        return make_response(response), 200


class UserEventsView(MethodView):
    """This class handles events creation and viewing of a single user"""

    @staticmethod
    def post():
        """Handle POST request for this view. Url ---> /api/events"""

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                BlacklistToken(token=access_token)
                # checks if the user_id has a valid token or contains the user id
                # Go ahead and handle the request, the user is authed
                user = User.query.filter_by(id=user_id).first_or_404()
                if user.email_confirmed is not True:
                    response = {
                        "message":'Your Must Confirm your Email Address in-order to create an event'
                    }
                    return make_response(jsonify(response)), 401

                args = {}
                event_models = [
                    'title', 'location', 'time', 'date',
                    'description', 'image_url', 'event_category'
                ]

                for event_res in event_models:
                    var = str(request.data.get(event_res, '').capitalize())
                    var = var.strip(' \t\n\r')
                    if not var:
                        response = {
                            "message":'{} missing'.format(event_res)
                        }
                        return make_response(jsonify(response)), 401
                    args.update({event_res:var})

                if Events.query.filter_by(title=args['title']).first():
                    response = {
                        "message":'Event title exists. Choose another one'
                    }
                    return make_response(jsonify(response)), 401

                event = Events(
                    **args,
                    created_by=user_id)

                event.save()
                response = jsonify({
                    'id': event.id,
                    'title': event.title,
                    'location': event.location,
                    'time': event.time,
                    'date': event.date,
                    'description': event.description,
                    'image_url':event.image_url,
                    'created_by': user_id,
                    'event_category': event.event_category,

                })

                return make_response(response), 201

            response_object = {
                'status': 'fail',
                'message': user_id
            }
            return make_response(jsonify(response_object)), 401

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @staticmethod
    def get():
        """Handle GET request for this view. Url ---> /api/events"""

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                BlacklistToken(token=access_token)
                # get all the events for this user
                categories = EventCategory.get__all_categories()
                page = request.args.get('page', default=1, type=int)
                limit = request.args.get('limit', default=10, type=int)

                events = Events.get_all_user(user_id)

                event_page = events.paginate(page, limit, False).items
                results = []

                for event in event_page:
                    for category in categories:
                        event.event_category = category.category_name
                    obj = {
                        'id': event.id,
                        'title': event.title,
                        'location': event.location,
                        'time': event.time,
                        'date': event.date,
                        'description': event.description,
                        'image_url':event.image_url,
                        'event_category':event.event_category
                    }
                    results.append(obj)

                if not results:
                    response = {
                        'message': "No events found"
                    }
                    return make_response(jsonify(response)), 404

                return make_response(jsonify(results)), 200

            response_object = {
                'status': 'fail',
                'message': user_id
            }
            return make_response(jsonify(response_object)), 401

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401


class EventsManupilationView(MethodView):
    """This class handles all methods that involve single event
    get, update and delete. Url --->/api/events/<int:event_id>"""

    @staticmethod
    def get(event_id):
        """Handles single event data with GET by event id."""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]
        categories = EventCategory.get__all_categories()

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                BlacklistToken(token=access_token)
                # retrieve an event using it's ID
                event = Events.query.filter_by(id=event_id).first_or_404()
                if user_id is not event.created_by:
                    response = {
                        'message': 'Your do not have authorization to access this event privately'
                    }
                    return make_response(jsonify(response)), 401
                for category in categories:
                    event.event_category = category.category_name
                response = jsonify({
                    'id': event.id,
                    'title': event.title,
                    'location': event.location,
                    'time': event.time,
                    'date': event.date,
                    'description': event.description,
                    'image_url':event.image_url,
                    'created_by': event.created_by,
                    'event_category':event.event_category
                })
                return make_response(response), 200

            response_object = {
                'status': 'fail',
                'message': user_id
            }
            return make_response(jsonify(response_object)), 401
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @staticmethod
    def put(event_id):
        """This function handles editing of single events by their id"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                BlacklistToken(token=access_token)
                # retrieve an event using it's ID
                event = Events.query.filter_by(id=event_id).first_or_404()
                if user_id is not event.created_by:
                    response = {
                        'message': 'Your do not have authorization to access this event privately'
                    }
                    return make_response(jsonify(response)), 401

                title = str(request.data.get('title', ''))
                location = str(request.data.get('location', ''))
                time = str(request.data.get('time', ''))
                date = str(request.data.get('date', ''))
                description = str(request.data.get('description', ''))
                image_url = str(request.data.get('image_url', ''))
                event_category = str(request.data.get('event_category', ''))

                event.title = title
                event.location = location
                event.time = time
                event.date = date
                event.description = description
                event.image_url = image_url
                event.event_category = event_category

                event.save()
                response = {
                    'id': event.id,
                    'title': event.title,
                    'location': event.location,
                    'time': event.time,
                    'date': event.date,
                    'description': event.description,
                    'image_url':event.image_url,
                    'created_by': event.created_by,
                    'event_category': event.event_category
                }
                return make_response(jsonify(response)), 200

            response_object = {
                'status': 'fail',
                'message': user_id
            }
            return make_response(jsonify(response_object)), 401

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @staticmethod
    def delete(event_id):
        """This Handles deleting of an event with it's id"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                BlacklistToken(token=access_token)
                # retrieve an event using it's ID
                event = Events.query.filter_by(id=event_id).first_or_404()
                if user_id is not event.created_by:
                    response = {
                        'message': 'Your do not have authorization to access this event privately'
                    }
                    return make_response(jsonify(response)), 401

                event.delete()
                return {
                    "message": "event {} deleted successfully".format(event.id)
                }, 200

            response_object = {
                'status': 'fail',
                'message': user_id
            }
            return make_response(jsonify(response_object)), 401

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401


class EventRsvpView(MethodView):
    """This class handles POST method for user
    RSVP to and event in url, ----> /api/events/<int:event_id>/rsvp"""

    @staticmethod
    def post(event_id):
        """Adds a user to rsvp to a specific event."""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                BlacklistToken(token=access_token)
                event = Events.query.filter_by(id=event_id).first_or_404()
                print(event)
                # POST User to the RSVP
                user = User.query.filter_by(id=user_id).first_or_404()
                has_prev_rsvpd = event.add_rsvp(user)
                if has_prev_rsvpd:
                    response = {
                        'message': 'You have already reserved a seat'
                    }
                    return make_response(jsonify(response)), 202
                msg = Message(
                    "RSVP to an Event",
                    sender="tonny.nesh@gmail.com",
                    recipients=["tonnie.nesh@gmail.com"]
                )

                msg.html = """
                        You have reserved a seat to attend <h3>{}</h3> on {} {} at {}.
                """.format(event.title, event.date, event.time, event.location)
                MAIL.send(msg)

                response = {
                    'message': 'You have Reserved a seat'
                }
                return make_response(jsonify(response)), 200

            response_object = {
                'status': 'fail',
                'message': user_id
            }
            return make_response(jsonify(response_object)), 401

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401


class EventCategories(MethodView):
    """This class handles category creation and viewing"""

    @staticmethod
    def post():
        """Handle POST request for this view. Url ---> /api/cartegory"""

        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                BlacklistToken(token=access_token)
                # checks if the user_id has a valid token or contains the user id
                # Go ahead and handle the request, the user is authed

                args = {}
                event_models = ['category_name']

                for event_res in event_models:
                    var = str(request.data.get(event_res, '').capitalize())
                    if not var:
                        response = {
                            "message":'{} missing'.format(event_res)
                        }
                        return make_response(jsonify(response)), 401
                    args.update({event_res:var})

                if EventCategory.check_category(category_name=args['category_name']):
                    response = {
                        "message":'Category name exists. Choose another one'
                    }
                    return make_response(jsonify(response)), 401

                category = EventCategory(**args)

                category.save()
                response = jsonify({
                    'id': category.id,
                    'category_name': category.category_name
                })

                return make_response(response), 201

            response_object = {
                'status': 'fail',
                'message': user_id
            }
            return make_response(jsonify(response_object)), 401
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    @staticmethod
    def get():
        """Handle GET request for this view. Url ---> /api/category"""
        categories = EventCategory.get__all_categories()

        results = []

        for category in categories:
            obj = {
                'id': category.id,
                'category_name': category.category_name
            }
            results.append(obj)

        if not results:
            response = {
                'message': "Add a new category"
            }
            return make_response(jsonify(response)), 404

        return make_response(jsonify(results)), 200

# Define the API resource
ALL_EVENTS_VIEW = AllEventsView.as_view('ALL_EVENTS_VIEW')
SINGLE_EVENT_VIEW = SingleEventView.as_view('SINGLE_EVENT_VIEW')
USER_EVENTS_VIEW = UserEventsView.as_view('USER_EVENTS_VIEW')
EVENT_MANUPILATION_VIEW = EventsManupilationView.as_view('EVENT_MANUPILATION_VIEW')
EVENT_RSVP_VIEW = EventRsvpView.as_view('EVENT_RSVP_VIEW')
EVENT_CATEGORIES_VIEW = EventCategories.as_view('EVENT_CATEGORIES_VIEW')

# Define the rule for view all events url --->  /api/events/all
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/events/all',
    view_func=ALL_EVENTS_VIEW,
    methods=['GET'])

# Define the rule for view all events url --->  /api/events/all/<int:event_id>
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/events/all/<int:event_id>',
    view_func=SINGLE_EVENT_VIEW,
    methods=['GET'])

# Define the rule for view all events url --->  /api/events
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/events',
    view_func=USER_EVENTS_VIEW,
    methods=['POST'])

events_blueprint.add_url_rule(
    '/api/events',
    view_func=USER_EVENTS_VIEW,
    methods=['GET'])


# Define the rule for view all events url --->  /api/events/<int:event_id>
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/events/<int:event_id>',
    view_func=EVENT_MANUPILATION_VIEW,
    methods=['GET'])

events_blueprint.add_url_rule(
    '/api/events/<int:event_id>',
    view_func=EVENT_MANUPILATION_VIEW,
    methods=['PUT'])

events_blueprint.add_url_rule(
    '/api/events/<int:event_id>',
    view_func=EVENT_MANUPILATION_VIEW,
    methods=['DELETE'])

# Define the rule for view all events url --->  /api/events/<int:event_id>/rsvp
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/events/<int:event_id>/rsvp',
    view_func=EVENT_RSVP_VIEW,
    methods=['POST'])

# Define the rule for view all events url --->  /api/category
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/category',
    view_func=EVENT_CATEGORIES_VIEW,
    methods=['POST'])

events_blueprint.add_url_rule(
    '/api/category',
    view_func=EVENT_CATEGORIES_VIEW,
    methods=['GET'])
