"""import depancies and methods."""

from flask_api import FlaskAPI
from flask_sqlalchemy import SQLAlchemy

# local import
from instance.config import app_config

# initialize sql-alchemy
db = SQLAlchemy()

def create_app(config_name):
    """Creates a new Flask object and returns when it's configured
    and connected with the db."""

    app = FlaskAPI(__name__, instance_relative_config=True)

    app.config.from_object(app_config[config_name])
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)


    # import the authentication blueprint and register it on the app
    from .auth import auth_blueprint
    app.register_blueprint(auth_blueprint)

    from .events import events_blueprint
    app.register_blueprint(events_blueprint)

    return app
