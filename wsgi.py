#!/usr/bin/env python
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

import logging

from flup.server.fcgi import WSGIServer
from talkatv import app

# Explicitly set app.debug to false, otherwise flask will swallow any exceptions
# that are raised from the app.
app.debug = False

if __name__ == '__main__':
    # Set up logging, even though app.debug is off we'll probably want the logs.
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter(app.debug_log_format))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.DEBUG)

    app.logger.info('Starting WSGI server on {0}'.format(
        app.config['WSGI_BIND_ADDR']))
    WSGIServer(app, bindAddress=app.config['WSGI_BIND_ADDR']).run()
