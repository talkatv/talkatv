from flask.ext.wtf import Form, html5, TextField, PasswordField, validators
from desqus.db import User, Item, Comment
from desqus.tools.redirect import RedirectForm


class RegistrationForm(Form):
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])
    email = html5.EmailField('Email', [validators.Required()])

    def __init__(self, *args, **kw):
        Form.__init__(self, *args, **kw)
        self.user = None

    def validate(self):
        if not Form.validate(self):
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
    username = TextField('Username', [validators.Required()])
    password = PasswordField('Password', [validators.Required()])

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.user = None

    def validate(self):
        if not Form.validate(self):
            return False

        user = User.query.filter_by(username=self.username.data).first()

        if user is None:
            self.username.errors.append('Unknown username')
            return False

        if not user.check_password(self.password.data):
            self.password.errors.append('Invalid password')
            return False

        self.user = user
        return True
