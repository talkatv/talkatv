import os
import subprocess

from desqus import app


DOCS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'docs')


def build_docs():
    try:
        app.logger.info('Building docs')
        subprocess.check_call(['make', 'html'], cwd=DOCS_DIR)
    except subprocess.CalledProcessError:
        app.logger.warn('Couldn\'t build docs')


if not os.path.isdir(os.path.join(DOCS_DIR, 'build', 'html')):
    build_docs()


app.debug = True
app.run(port=4547)
