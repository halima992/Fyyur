import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

# Connect to the database


# TODO IMPLEMENT DATABASE URL
#SQLALCHEMY_DATABASE_URI = '<Put your local database url>'
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:62328243@localhost:5432/fyyurapp'

SQLALCHEMY_TRACK_MODIFICATIONS = DEBUG

# TODO delete app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:62328243@localhost:5432/todoapp'

