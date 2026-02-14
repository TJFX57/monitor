import os
from flask import Flask
from application import database
from display import Display
from atexit import register

display = Display(mode='s')

def exit_app():
    display.__exit__(None, None, None)

def init_app():
    display.__enter__()
    register(exit_app)

    app = Flask(__name__)

    # enable instance relative configuration
    app = Flask(__name__, instance_relative_config=True)
    
    # set secret key for sessions and flash messages
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

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