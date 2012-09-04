#!/usr/bin/env python
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

import logging

from mig import run
from mig.models import MigrationData

from talkatv import db
from talkatv.models import MODELS
from talkatv.migrations import MIGRATIONS

root_log = logging.getLogger()
root_log.setLevel(logging.DEBUG)
logging.basicConfig()

_log = logging.getLogger(__name__)


def check_or_create_mig_data():
    if not db.engine.dialect.has_table(db.session, 'mig__data'):
        _log.info('Creating MigrationData table...')
        MigrationData.__table__.create(db.engine)

        # Create the first migration, so that mig doesn't init.
        migration = MigrationData(name=u'__main__', version=0)
        db.session.add(migration)
        db.session.commit()


if __name__ == '__main__':
    if db.engine.dialect.has_table(db.session, 'user'):
        # The DB is already populated, check if migrations are active
        check_or_create_mig_data()

    run(db.engine, u'__main__', MODELS, MIGRATIONS)
