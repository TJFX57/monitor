# Standard library
import os
from atexit import register

# Third-party
from flask import Flask

# Local application imports
from application import database
from display import Display, BLUE, GREEN, RED

display = Display(mode='s')


def exit_app():
    display.__exit__(None, None, None)


def init_app():
    display.__enter__()
    register(exit_app)

    # Create app ONCE
    app = Flask(__name__, instance_relative_config=True)

    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'dev-secret-key-change-in-production'
    )

    # Ensure instance folder exists
    os.makedirs(app.instance_path, exist_ok=True)

    # LED Request Hooks
    @app.before_request
    def before_request():
        display.set_colour(BLUE)

    @app.after_request
    def after_request(response):
        display.set_colour(GREEN)
        return response

    @app.teardown_request
    def teardown_request(exception):
        if exception:
            display.set_colour(RED)

    # Init database
    database.init_app(app)

    with app.app_context():
        from . import routes
        database.init_database()

    return app