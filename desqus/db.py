# desqus - Commenting backend for static pages
# Copyright (C) 2012  desqus contributors, see AUTHORS
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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

    def __init__(self, url, title, owner=None, created=None):
        if owner:
            self.owner = owner

        self.title = title
        self.url = url

        if not created:
            self.created = datetime.utcnow()
        else:
            self.created = created

    def as_dict(self):
        me = {
                'id': self.id,
                'title': self.title,
                'url': self.url,
                'created': self.created.isoformat()}
        if self.owner:
            me.update({'owner': self.owner.id})

        return me


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

    def as_dict(self):
        me = {
                'item': self.item.id,
                'user_id': self.user.id,
                'username': self.user.username,
                'text': self.text,
                'created': self.created.isoformat()}
        return me
