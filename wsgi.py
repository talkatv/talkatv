#!/usr/bin/env python
from flup.server.fcgi import WSGIServer
from desqus import app

app.debug = True

if __name__ == '__main__':
    bind_address = '/tmp/desqus.sock'
    app.logger.info('Starting WSGI server on {0}'.format(bind_address))
    WSGIServer(app, bindAddress=bind_address).run()
