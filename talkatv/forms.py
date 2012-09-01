# talkatv - Commenting backend for static pages
# Copyright (C) 2012  talkatv contributors, see AUTHORS
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

from pywebfinger import finger

from flask import g

from flask.ext.wtf import Form, html5, TextField, PasswordField, HiddenField, \
        validators
from talkatv.models import User, Item, Comment, OpenID
from talkatv.tools.redirect import RedirectForm


class RegistrationForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Optional()])
    email = html5.EmailField('Email', [validators.Required()])

    def __init__(self, *args, **kw):
        Form.__init__(self, *args, **kw)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        if not self.password.data and not self.openid.data:
            self.errors.append(
                    'You must include either password or an OpenID URL')
            return False

        user = User.query.filter_by(username=self.username.data).first()

        if user is not None:
            self.username.errors.append('User already exists.')

        return True


class ProfileForm(Form):
    '''
    Edit user profile form
    '''
    username = TextField('Username', [validators.Required()])
    email = html5.EmailField('Email', [validators.Required()])
    openid = html5.URLField('OpenID', [validators.Optional()])

    def __init__(self, *args, **kw):
        Form.__init__(self, *args, **kw)

    def validate(self):
        if not Form.validate(self):
            return False

        user_exists = User.query.filter(
                User.username==self.username.data).filter(
                        User.email!=g.user.email).count()

        if user_exists:
            self.username.errors.append(
                    'The username "{0}" is already taken'.format(
                        self.username.data))
            return False

        email_exists = User.query.filter(
                User.email==self.email.data).filter(
                        User.username!=g.user.username).count()

        if email_exists:
            self.email.errors.append(
                    'The email "{0}" is already taken'.format(
                        self.email.data))
            return False

        return True


class ChangePasswordForm(Form):
    password = PasswordField('Password',
            [validators.Optional()])
    new_password = PasswordField('New password', [validators.Required()])

    def __init__(self, *args, **kw):
        Form.__init__(self, *args, **kw)

    def validate(self):
        if not Form.validate(self):
            return False

        if g.user.password is not None:
            if not g.user.check_password(self.password.data):
                self.password.errors.append('Invalid password')

        return True


class ItemForm(Form):
    url = TextField('Page URL', [validators.Required()])
    title = TextField('Page title', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.item = None

    def validate(self):
        if not Form.validate(self):
            return False

        item = Item.query.filter_by(url=self.url.data).first()

        if item is not None:
            self.url.errors.append('That URL already exists')
            return False

        return True


class SiteForm(Form):
    url = html5.URLField('URL', [validators.Required()])
    name = TextField('Name', [validators.Optional()])


class LoginForm(RedirectForm):
    username = TextField('Username', [validators.Optional()])
    password = PasswordField('Password', [validators.Optional()])
    openid = TextField('OpenID', [validators.Optional()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        RedirectForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        user = None

        openid_identifier = None

        # Account for webfinger addresses in OpenID input and fetch the OpenID
        # identifier from the webfinger identity
        if '@' in self.openid.data:
            webfinger = finger(self.openid.data)

            if not webfinger.open_id:
                self.webfinger.errors.append(
                        'Can\'t find any OpenID identifier for {0}'.format(
                            self.webfinger.data))
            else:
                openid_identifier = webfinger.open_id

        self.openid.data = self.openid.data or openid_identifier

        if openid_identifier or self.openid.data:
            openid = OpenID.query.filter_by(url=self.openid.data).first()

            if not openid:
                self.openid.errors.append('Unknown OpenID URL {0}'.format(
                    self.openid.data))
            else:
                user = openid.user

        if self.username.data and self.password.data:
            user = User.query.filter_by(username=self.username.data).first()

            if user is None:
                self.username.errors.append('Unknown username')
            elif not user.check_password(self.password.data):
                self.password.errors.append('Invalid password')

        if user:
            self.user = user
            return True

        return False
