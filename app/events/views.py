"""import depancies and methods."""

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User, Events, EventCategory

from . import events_blueprint


class AllEventsView(MethodView):
    """This class gets all events with out token validation."""

    @staticmethod
    def get():
        """Handle POST request for this view. Url ---> /api/events/all"""

        # GET all the events for this user
        events = Events.query
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=10, type=int)
        q = request.args.get('q')

        args = {}
        potential_search = ['location', 'category']

        for search_res in potential_search:
            var = request.args.get(search_res)
            if var:
                args.update({search_res:var})

        if q:
            evnt = Events.query.filter(Events.title.ilike('%{}%'.format(q)))
            event_page = evnt.paginate(page, limit, False).items

            results = []

            for event in event_page:
                obj = {
                    'id': event.id,
                    'title': event.title,
                    'location': event.location,
                    'time': event.time,
                    'date': event.date,
                    'description': event.description,
                    'category':event.category,
                    'image_url':event.image_url
                }
                results.append(obj)

            if not results:
                response = {
                    'message': "No events found"
                }
                return make_response(jsonify(response)), 404

            return make_response(jsonify(results)), 200

        else:
            events = Events.query.filter_by(**args)


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
                'category':event.category,
                'image_url':event.image_url
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
        response = jsonify({
            'id': event.id,
            'title': event.title,
            'location': event.location,
            'time': event.time,
            'date': event.date,
            'description': event.description,
            'category':event.category,
            'image_url':event.image_url,
            'created_by': event.created_by
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
                # checks if the user_id has a valid token or contains the user id
                # Go ahead and handle the request, the user is authed

                args = {}
                event_models = [
                    'title', 'location', 'category', 'time', 'date', 'description', 'image_url'
                ]

                for event_res in event_models:
                    var = str(request.data.get(event_res, '').capitalize())
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
                    'category':event.category,
                    'image_url':event.image_url,
                    'created_by': user_id
                })

                return make_response(response), 201
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
                # get all the events for this user
                page = request.args.get('page', default=1, type=int)
                limit = request.args.get('limit', default=10, type=int)

                events = Events.get_all_user(user_id)

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
                        'category':event.category,
                        'image_url':event.image_url
                    }
                    results.append(obj)

                if not results:
                    response = {
                        'message': "No events found"
                    }
                    return make_response(jsonify(response)), 404

                return make_response(jsonify(results)), 200

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

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
                # retrieve an event using it's ID
                event = Events.query.filter_by(id=event_id).first_or_404()
                if user_id is not event.created_by:
                    response = {
                        'message': 'Your do not have authorization to access this event privately'
                    }
                    return make_response(jsonify(response)), 401
                response = jsonify({
                    'id': event.id,
                    'title': event.title,
                    'location': event.location,
                    'time': event.time,
                    'date': event.date,
                    'description': event.description,
                    'category':event.category,
                    'image_url':event.image_url,
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

    @staticmethod
    def put(event_id):
        """This function handles editing of single events by their id"""
        auth_header = request.headers.get('Authorization')
        access_token = auth_header.split(" ")[1]

        if access_token:
            user_id = User.decode_token(access_token)
            if not isinstance(user_id, str):
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
                category = str(request.data.get('category', ''))
                image_url = str(request.data.get('image_url', ''))

                event.title = title
                event.location = location
                event.time = time
                event.date = date
                event.description = description
                event.category = category
                event.image_url = image_url

                event.save()
                response = {
                    'id': event.id,
                    'title': event.title,
                    'location': event.location,
                    'time': event.time,
                    'date': event.date,
                    'description': event.description,
                    'category':event.category,
                    'image_url':event.image_url,
                    'created_by': event.created_by
                }
                return make_response(jsonify(response)), 200

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

        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401


class EventRsvpView(MethodView):
    """This class handles POST method for user
    RSVP to and event in url, ----> /api/events/<int:event_id>/rsvp/"""

    @staticmethod
    def post(event_id):
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

                event = EventCategory(**args,)

                event.save()
                response = jsonify({
                    'id': event.id,
                    'category_name': event.category_name
                })

                return make_response(response), 201
        else:
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401

    # @staticmethod
    # def get():
    #     """Handle GET request for this view. Url ---> /api/events"""

    #     auth_header = request.headers.get('Authorization')
    #     access_token = auth_header.split(" ")[1]

    #     if access_token:
    #         user_id = User.decode_token(access_token)
    #         if not isinstance(user_id, str):
    #             # get all the events for this user
    #             page = request.args.get('page', default=1, type=int)
    #             limit = request.args.get('limit', default=10, type=int)

    #             events = Events.get_all_user(user_id)

    #             event_page = events.paginate(page, limit, False).items
    #             results = []

    #             for event in event_page:
    #                 obj = {
    #                     'id': event.id,
    #                     'title': event.title,
    #                     'location': event.location,
    #                     'time': event.time,
    #                     'date': event.date,
    #                     'description': event.description,
    #                     'category':event.category,
    #                     'image_url':event.image_url
    #                 }
    #                 results.append(obj)

    #             if not results:
    #                 response = {
    #                     'message': "No events found"
    #                 }
    #                 return make_response(jsonify(response)), 404

    #             return make_response(jsonify(results)), 200

    #     else:
    #         # user is not legit, so the payload is an error message
    #         message = user_id
    #         response = {
    #             'message': message
    #         }
    #         return make_response(jsonify(response)), 401

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
