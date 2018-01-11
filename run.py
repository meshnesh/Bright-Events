import os

from app import create_app
from flasgger import Swagger

config_name = os.getenv('APP_SETTINGS') # config_name = "development"
app = create_app(config_name)

Swagger(app, template_file="docs/docs.yml")

if __name__ == '__main__':
    app.run()
    