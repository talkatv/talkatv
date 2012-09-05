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

from mig import RegisterMigration

from sqlalchemy import MetaData, Table, Column, Integer, Unicode, DateTime, \
        ForeignKey

MIGRATIONS = {}


@RegisterMigration(1, MIGRATIONS)
def create_site_table(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    user_table = Table('user', metadata, autoload=True,
            autoload_with=db_conn.bind)

    site_table = Table('site', metadata,
            Column('id', Integer, primary_key=True),
            Column('domain', Unicode),
            Column('owner_id', Integer, ForeignKey(user_table.columns['id'])))

    site_table.create()

    db_conn.commit()


@RegisterMigration(2, MIGRATIONS)
def item_add_site_id(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    item_table = Table('item', metadata, autoload=True)
    site_table = Table('site', metadata, autoload=True)

    site_id_col = Column('site_id', Integer, ForeignKey(
        site_table.columns['id']))

    site_id_col.create(item_table)

    db_conn.commit()


@RegisterMigration(3, MIGRATIONS)
def add_site_created_remove_item_owner(db_conn):
    metadata = MetaData(bind=db_conn.bind)

    site_table = Table('site', metadata, autoload=True)

    created_col = Column('created', DateTime)

    created_col.create(site_table)

    item_table = Table('item', metadata, autoload=True)

    item_table.columns['owner_id'].drop()

    db_conn.commit()


@RegisterMigration(4, MIGRATIONS)
def comment_add_reply_to_id(db):
    metadata = MetaData(bind=db.bind)

    comment_table = Table('comment', metadata, autoload=True)
    reply_to_column = Column('reply_to_id', Integer, ForeignKey('comment.id'))

    reply_to_column.create(comment_table)

    db.commit()
