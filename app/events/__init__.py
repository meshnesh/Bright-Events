"""import depancies and methods."""

from flask import Blueprint

# This instance of a Blueprint that represents the authentication blueprint
events_blueprint = Blueprint('event', __name__)


from . import views