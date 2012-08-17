import os

from flask import Flask
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)

app.debug = True


if os.path.exists('config_local.py'):
    # Flask uses a different path than os.path.exist()
    app.config.from_pyfile('../config_local.py')
    app.logger.info(app.config)
else:
    app.config.from_pyfile('../config.py')
    app.logger.info(app.config)

Bootstrap(app)

import desqus.views
