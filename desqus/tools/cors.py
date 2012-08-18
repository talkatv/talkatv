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

import flask
from flask import request
from desqus import app


def jsonify(**kw):
    response = flask.jsonify(**kw)

    callback = request.args.get('callback')

    if callback:
        response.response.insert(0, '{0}('.format(callback))
        response.response.append(');')

    response.headers['Access-Control-Allow-Origin'] = \
            app.config['CORS_ALLOW_ORIGIN']
    response.headers['Access-Control-Allow-Credentials'] = \
            app.config['CORS_ALLOW_CREDENTIALS']
    response.headers['Access-Control-Max-Age'] = \
            app.config['CORS_MAX_AGE']
    response.headers['Access-Control-Allow-Headers'] = \
            app.config['CORS_ALLOW_HEADERS']
    response.headers['Access-Control-Allow-Methods'] = \
            app.config['CORS_ALLOW_METHODS']

    return response
