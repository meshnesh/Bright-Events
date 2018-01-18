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


# Define the API resource
ALL_EVENTS_VIEW = AllEventsView.as_view('ALL_EVENTS_VIEW')

# Define the rule for view all events url --->  /api/events/all
# Then add the rule to the blueprint
events_blueprint.add_url_rule(
    '/api/events/all',
    view_func=ALL_EVENTS_VIEW,
    methods=['GET'])
