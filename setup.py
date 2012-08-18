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

from setuptools import setup, find_packages

READMEFILE = 'README.rst'


setup(
        name='desqus',
        version='0.1-dev',
        packages=find_packages(),
        install_requires=[
            'flask',
            'Flask-SQLAlchemy',
            'flask-bootstrap',
            'Flask-WTF',
            'py-bcrypt',
            'flup',
            'sphinx'],
        author_email='joar@desqus.org',
        url='http://desqus.org',
        long_description=open(READMEFILE).read(),
        classifiers=[
            'Development Status :: 3 - Alpha',
            'Environment :: Web Environment',
            'Programming Language :: Python'],
        )
