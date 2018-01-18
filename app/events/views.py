"""import depancies and methods."""

from flask.views import MethodView
from flask import make_response, request, jsonify
from app.models import User, Events

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

        args = {}
        potential_search = ['title', 'location', 'cartegory']

        for search_res in potential_search:
            var = request.args.get(search_res)
            if var:
                args.update({search_res:var})

        if args:
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
            # user is not legit, so the payload is an error message
            message = user_id
            response = {
                'message': message
            }
            return make_response(jsonify(response)), 401




# Define the API resource
ALL_EVENTS_VIEW = AllEventsView.as_view('ALL_EVENTS_VIEW')
USER_EVENTS = UserEventsView.as_view('USER_EVENTS')

# Define the rule for view all events url --->  /api/events/all
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/events/all',
    view_func=ALL_EVENTS_VIEW,
    methods=['GET'])

events_blueprint.add_url_rule(
    '/api/events',
    view_func=USER_EVENTS,
    methods=['POST'])
