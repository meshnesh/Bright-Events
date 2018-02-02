"""import depancies and methods."""

import os

from app import create_app
from flask_mail import Mail

CONFIG_NAME = os.getenv('APP_SETTINGS')
APP = create_app(CONFIG_NAME)
MAIL = Mail(APP)

if __name__ == '__main__':
    APP.run()
