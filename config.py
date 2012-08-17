import os
import bcrypt

SQLALCHEMY_DATABASE_URI = 'sqlite:///{0}/desqus.db'.format(
        os.path.dirname(__file__))

SECRET_KEY = bcrypt.gensalt()
