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

import re
import os

from setuptools import setup, find_packages

READMEFILE = 'README.rst'
VERSIONFILE = os.path.join('talkatv', '_version.py')
VSRE = r'^__version__ = [\'"]([^\'"]*)[\'"]'


def get_version():
    '''
    Author: GNU MediaGoblin contributors
    '''
    verstrline = open(VERSIONFILE, "rt").read()
    mo = re.search(VSRE, verstrline, re.M)

    if mo:
        return mo.group(1)
    else:
        raise RuntimeError("Unable to find version string in %s." %
                           VERSIONFILE)


if __name__ == '__main__':
    setup(
            name='talkatv',
            version=get_version(),
            packages=find_packages(),
            install_requires=[
                'flask',
                'Flask-SQLAlchemy',
                'flask-bootstrap',
                'Flask-WTF',
                'Flask-OpenID',
                'py-bcrypt',
                'python-webfinger',
                'mig',
                'flup',
                'raven',
                'blinker',
                'sphinx'],
            author_email='joar@talka.tv',
            license='AGPLv3',
            url='http://talka.tv',
            long_description=open(READMEFILE).read(),
            classifiers=[
                'Development Status :: 3 - Alpha',
                'Licesnse :: OSI Approved :: GNU Affero General Public License',
                'Environment :: Web Environment',
                'Programming Language :: Python'],
            )
