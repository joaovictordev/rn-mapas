DEBUG = True

SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:3333@localhost/rnmapas'
SQLALCHEMY_TRACK_MODIFICATIONS = True

SECRET_KEY = 'themustsecretkey'

UPLOAD_FOLDER = '/app/uploads'
MAX_CONTENT_LENGTH = 16 * 1024 * 1024