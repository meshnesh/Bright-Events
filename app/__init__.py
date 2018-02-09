"""import depancies and methods."""

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

from flask import make_response, jsonify
from flask_mail import Mail

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()
mail = Mail()

def create_app(config_name):
    """Creates a new Flask object and returns when it's configured
    and connected with the db."""

    app = FlaskAPI(__name__, instance_relative_config=True, template_folder="templates")

    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    mail.init_app(app)


    @app.errorhandler(404)
    def not_found_error(error):
        response_object = {
            'message': 'Object not found'
        }
        print('manenos')
        return make_response(jsonify(response_object)), 404

    @app.errorhandler(405)
    def method_error(error):
        response_object = {
            'message': 'Check the method'
        }
        return make_response(jsonify(response_object)), 405

    @app.errorhandler(500)
    def internal_error(error):
        db.session.rollback()
        response_object = {
            'message': 'Oops error from our side, weare working to solve it'
        }
        return make_response(jsonify(response_object)), 500

    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .events import events_blueprint
    app.register_blueprint(events_blueprint)

    return app
