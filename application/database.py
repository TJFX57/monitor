import sqlite3
from flask import current_app
from flask import g

DATABASE_PATH = '/home/controller/data.db'
DATABASE_SCHEMA_PATH = '/home/controller/controller/schema.sql'

def get_database():
    database = getattr(g, '_database', None) 
    if database is None:
        database = g._database = sqlite3.connect(DATABASE_PATH)
        database.row_factory = sqlite3.Row
    return database

def init_database():
    database = get_database()
    with current_app.open_resource(DATABASE_SCHEMA_PATH, mode='r') as file:
        database.cursor().executescript(file.read())
    database.commit()

# peform a function directly on the database
def execute_database(query, args=()):
    cursor = get_database()
    cursor.execute(query, args)
    cursor.commit()

def query_database(query, args=(), one=False, names=False):
    cursor = get_database().execute(query, args)
    rows = cursor.fetchall()
    if names:
        names = [name[0] for name in cursor.description]
        rows.insert(0, names)
    cursor.close()
    return (rows[0] if rows else None) if one else rows

def close_database(e=None):
    database = getattr(g, '_database', None)
    if database is not None:
        database.close()

# function refrences to be access by the app's context manager
def init_app(app):
    app.teardown_appcontext(close_database)