from flask import Flask
from flask.ext.bootstrap import Bootstrap

app = Flask(__name__)
app.config.from_pyfile('../config.py')

Bootstrap(app)

import desqus.views
