import bcrypt

from datetime import datetime

from flask.ext.sqlalchemy import SQLAlchemy
from desqus import app

db = SQLAlchemy(app)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(60), unique=True)
    email = db.Column(db.String(255), unique=True)
    password = db.Column(db.String(60))

    def __init__(self, username, email, password=None):
        self.username = username
        self.email = email

        if password:
            self.set_password(password)

    def __repr__(self):
        return '<User {0}>'.format(self.username)

    def set_password(self, password):
        self.password = bcrypt.hashpw(password, bcrypt.gensalt())

    def check_password(self, password):
        return bcrypt.hashpw(password, self.password) == self.password


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String())
    url = db.Column(db.String(), unique=True)
    created = db.Column(db.DateTime)

    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    owner = db.relationship('User',
            backref=db.backref('items', lazy='dynamic'))

    def __init__(self, owner, title, url, created=None):
        self.owner = owner
        self.title = title
        self.url = url

        if not created:
            self.created = datetime.utcnow()
        else:
            self.created = created


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    created = db.Column(db.DateTime)
    text = db.Column(db.String())

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    item = db.relationship('Item',
            backref=db.backref('comments', lazy='dynamic'))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    user = db.relationship('User',
            backref=db.backref('comments', lazy='dynamic'))

    def __init__(self, item, user, text, created=None):
        self.item = item
        self.user = user
        self.text = text

        if not created:
            self.created = datetime.utcnow()
        else:
            self.created = created
