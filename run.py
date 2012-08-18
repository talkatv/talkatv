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
