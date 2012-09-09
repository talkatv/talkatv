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

from flask import request, json, abort, g

from talkatv import app
from talkatv.decorators import require_active_login
from talkatv.models import Item
from talkatv.tools.cors import jsonify, allow_all_origins
from talkatv.item import get_or_add_item
from talkatv.api import get_context, post_comment


@app.route('/api/comments', methods=['GET', 'POST', 'OPTIONS'])
@require_active_login(['POST'])
def api_comments():
    if request.method == 'OPTIONS':
        # We're dealing with a pre-flight request
        return jsonify(status='OK', _allow_origin_cb=allow_all_origins)

    if request.method == 'POST':
        post_data = json.loads(request.data)

        item = Item.query.filter_by(id=post_data['item']).first()

        if not item:
            return abort(404)

        comment = post_comment(item, post_data, g.user)

        return jsonify(
                comment=comment.as_dict(),
                status='OK',
                _allow_origin_cb=allow_all_origins)

    if not request.args.get('item_url'):
        return abort(404)

    item = get_or_add_item(
            request.args.get('item_url'),
            request.args.get('item_title'))

    return_data = get_context(item)

    return jsonify(_allow_origin_cb=allow_all_origins,
            **return_data)


@app.route('/api/check-login', methods=['GET', 'OPTIONS'])
def check_login():
    if g.user:
        return jsonify(status='OK', _allow_origin_cb=allow_all_origins)
    else:
        return jsonify(status=False, _allow_origin_cb=allow_all_origins)
