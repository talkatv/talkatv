import os
import subprocess
import logging

from desqus.views import app

_log = logging.getLogger(__name__)
_log.setLevel(logging.DEBUG)
logging.basicConfig()


DOCS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'docs')


def build_docs():
    try:
        _log.info('Building docs')
        subprocess.check_call(['make', 'html'], cwd=DOCS_DIR)
    except subprocess.CalledProcessError:
        _log.warn('Couldn\'t build docs')


if not os.path.isdir(os.path.join(DOCS_DIR, 'build', 'html')):
    build_docs()


app.debug = True
app.run(port=4547)
