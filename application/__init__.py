# Standard library
import os
from atexit import register

# Third-party
from flask import Flask

# Local application imports
from application import database
from display import Display, BLUE, GREEN, RED  # ← added colours

display = Display(mode='s')

def exit_app():
    display.__exit__(None, None, None)


def init_app():
    display.__enter__()
    register(exit_app)

    # enable instance relative configuration
    app = Flask(__name__, instance_relative_config=True)

    @app.before_request
    def before_request():
        # turn the LED blue at the start of the request
        display.set_colour(BLUE)

    @app.after_request
    def after_request(response):
        # turn the LED green after the request finishes
        display.set_colour(GREEN)
        return response

    @app.teardown_request
        # turn the LED red if there was an exception
    def teardown_request(exception):
        if exception:
            display.set_colour(RED)

    # set secret key for sessions and flash messages
    app.config['SECRET_KEY'] = os.environ.get(
        'SECRET_KEY',
        'dev-secret-key-change-in-production'
    )

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    database.init_app(app)

    with app.app_context():
        from . import routes
        database.init_database()
        return app