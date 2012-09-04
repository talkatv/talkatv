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

from urlparse import urlparse
from talkatv import db
from talkatv.models import Item, Site


def get_or_add_item(url, title=None):
    '''
    Get an item, add it if it doesn't exist.

    :param str url: item `URL`
    :param str title: item `title`
    '''
    item = Item.query.filter(Item.url == url).first()

    if not item:
        url_data = urlparse(url)

        # Get the parts of the domain, e.g. ['www', 'wandborg', 'se']
        # account for netlocs with a port number, e.g. wandborg.se:4547 by
        # removing that part before
        netloc_split = url_data.netloc.split(':')[0].split('.')

        site = None

        # Find a start position that is not further back than 7. This to prevent
        # malicious users from submitting '.a.a.a.a.a.a.a.a.a.a' * 7000 in an
        # attempt to overload the database.
        start = - (len(netloc_split) if len(netloc_split) < 8 else 7)
        # Addresses that are higher up than the second level can be safely
        # accounted for as invalid.
        stop = -2

        # Try to find a registered site for this item. Step through the URL
        for i in range(start, stop):
            site = Site.query.filter(Site.domain == '.'.join(netloc_split[i:]))\
                    .first()

            if site is not None:
                break

        item = Item(url, title, site)
        db.session.add(item)
        db.session.commit()

    return item
