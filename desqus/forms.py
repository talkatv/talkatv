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

from flask.ext.wtf import Form, html5, TextField, PasswordField, HiddenField, \
        validators
from desqus.models import User, Item, Comment, OpenID
from desqus.tools.redirect import RedirectForm


class RegistrationForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Optional()])
    email = html5.EmailField('Email', [validators.Required()])
    openid = html5.URLField('OpenID', [validators.Optional()])

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


class LoginForm(RedirectForm):
    username = TextField('Username', [validators.Optional()])
    password = PasswordField('Password', [validators.Optional()])
    openid = html5.URLField('OpenID', [validators.Optional()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        RedirectForm.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        user = None

        if self.openid.data:
            openid = OpenID.query.filter_by(url=self.openid.data).first()

            if not openid:
                self.openid.errors.append('Unknown OpenID URL')
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
