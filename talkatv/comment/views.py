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

from flask import render_template, abort, request, redirect, url_for

from talkatv import app
from talkatv.models import Item
from talkatv.api import get_context


@app.route('/comment/list/<int:item_id>')
@app.route('/comment/list/')
def comment_list(item_id=None):
    item = None

    if item_id:
        item = Item.query.filter_by(id=item_id).first()

        if item is None:
            return abort(404)
    else:
        if request.args.get('url'):
            item = Item.query.filter_by(url=request.args.get('url')).first()

            app.logger.debug('item by args[\'url\']: {0}'.format(item))

            if item:
                return redirect(url_for('comment_list', item_id=item.id))

        elif request.headers.get('Referer'):
            item = Item.query.filter_by(url=request.headers.get('Referer'))\
                    .first()

            if item:
                return redirect(url_for('comment_list', item_id=item.id))
            else:
                return abort(404)

    if item is None:
        return abort(404)

    comment_context = get_context(item)

    return render_template('talkatv/comment/list.html',
            comment_context=comment_context)
