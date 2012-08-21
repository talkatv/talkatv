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

from urlparse import urlparse, urlunparse

import flask

from flask import request
from desqus import app


def jsonify(_allow_origin_cb=None, **kw):
    response = flask.jsonify(**kw)

    callback = request.args.get('callback')

    if callback:
        response.response.insert(0, '{0}('.format(callback))
        response.response.append(');')

    if _allow_origin_cb:
        response.headers['Access-Control-Allow-Origin'] = \
                _allow_origin_cb(request.headers['Origin'])
    else:
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


def allow_all_origins(origin):
    '''
    This can be used to allow all origins, since * is prohibited if you use
    CORS with withCreadentials = true;

    Example:
        desqus.tools.cors.jsonify(_allow_origin_cb=allow_all_origins, **data)
    '''
    app.logger.debug(origin)
    return origin
