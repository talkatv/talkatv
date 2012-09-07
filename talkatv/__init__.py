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

import os

from flask import Flask
from flask.ext.bootstrap import Bootstrap
from flask.ext.openid import OpenID
from flask.ext.sqlalchemy import SQLAlchemy
from raven.contrib.flask import Sentry
from raven.handlers.logging import SentryHandler
from raven.conf import setup_logging

app = Flask(__name__)

app.config.from_pyfile('../config.py')

if os.path.exists('config_local.py'):
    # Flask uses a different path than os.path.exist()
    app.config.from_pyfile('../config_local.py')

Bootstrap(app)
oid = OpenID(app)
db = SQLAlchemy(app)

if 'SENTRY_DSN' in app.config or 'SENTRY_DSN' in os.environ:
    sentry = Sentry(app)
    handler = SentryHandler(sentry.client)
    setup_logging(handler)


# Let's begin the circular imports!
import talkatv.filters

import talkatv.views
import talkatv.profile.views
import talkatv.api.views
import talkatv.comment.views
import talkatv.site.views
