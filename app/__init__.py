# app/__init__.py

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

from flask import request, jsonify, abort, make_response

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    """Creates a new Flask object and returns when it's configured
    and connected with the db."""

    from app.models import Events

    app = FlaskAPI(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config.from_pyfile('config.py')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app)

    @app.route('/api/events/', methods=['POST', 'GET'])
    def event():
        """Function to handle POST and GET requests for events."""
        if request.method == "POST":
            title = str(request.data.get('title', ''))
            location = str(request.data.get('location', ''))
            time = str(request.data.get('time', ''))
            date = str(request.data.get('date', ''))
            description = str(request.data.get('description', ''))
            cartegory = str(request.data.get('cartegory', ''))
            imageUrl = str(request.data.get('imageUrl', ''))
            if title:
                event = Events(title=title, location=location,
                               time=time, date=date,
                               description=description,
                               cartegory=cartegory,
                               imageUrl=imageUrl)
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

                response.status_code = 201
                return response
        else:
            # GET
            events = Events.get_all_events()
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
            response = jsonify(results)
            response.status_code = 200
            return response

    return app
