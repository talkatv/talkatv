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

from flask.ext.wtf import Form, html5, TextField, validators


class SiteForm(Form):
    domain = TextField('Domain', [validators.Required()])

    def __init__(self, *args, **kw):
        Form.__init__(self, *args, **kw)

    def validate(self):
        if not Form.validate(self):
            return False

        if not re.match(r'^[a-z0-9.-]+$', self.domain.data):
            self.domain.errors.append(
                    'The domain name may only contain alphanumeric\
                    characters and hyphens or dots.')

            return False

        if not '.' in self.domain.data:
            self.domain.errors.append(
                    'Valid domains usually have at least one dot (.) in them')
            return False

        return True
