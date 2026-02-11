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

    database.init_app(app)

    with app.app_context():
        from . import routes
        database.init_database()
        return app