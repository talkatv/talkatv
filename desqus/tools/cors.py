import flask
from flask import request
from desqus import app


def jsonify(**kw):
    response = flask.jsonify(**kw)

    callback = request.args.get('callback')

    if not callback:
        app.logger.debug('No callback arg')
    else:
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
