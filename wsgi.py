#!/usr/bin/env python
from flup.server.fcgi import WSGIServer
from desqus import app

app.debug = True

if __name__ == '__main__':
    app.logger.info('Starting WSGI server on {0}'.format(
        app.config['WSGI_BIND_ADDR']))
    WSGIServer(app, bindAddress=app.config['WSGI_BIND_ADDR']).run()
