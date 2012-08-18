import os
import bcrypt

SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}/desqus.db'.format(
        os.path.dirname(__file__))

SECRET_KEY = bcrypt.gensalt()

WSGI_BIND_ADDR = '127.0.0.1', 45474

CORS_ALLOW_ORIGIN = 'http://80.joar.pagekite.me'
CORS_MAX_AGE = 3600
CORS_ALLOW_HEADERS = 'Accept, Content-Type, Connection, Cookie'
CORS_ALLOW_METHODS = 'GET, POST'
CORS_ALLOW_CREDENTIALS = 'true'
