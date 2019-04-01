import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = True

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:3333@localhost/rnmapas'
SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = 'themustsecretkey'