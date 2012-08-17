import os
import bcrypt

SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}/desqus.db'.format(
        os.path.dirname(__file__))

SECRET_KEY = bcrypt.gensalt()

WSGI_BIND_ADDR = '127.0.0.1', 45474
