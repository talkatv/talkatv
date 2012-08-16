import os
import subprocess

from desqus.views import app

DOCS_DIR = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'docs')


def build_docs():
    subprocess.check_call(['make', 'html'], cwd=DOCS_DIR)


if not os.path.isdir(os.path.join(DOCS_DIR, 'build', 'html')):
    build_docs()


app.debug = True
app.run(port=4547)
