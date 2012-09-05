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

from talkatv import app, db
from talkatv.decorators import require_active_login
from talkatv.models import Item, Comment, User
from talkatv.tools.cors import jsonify, allow_all_origins
from talkatv.notification import send_comment_notification
from talkatv.item import get_or_add_item


@app.route('/api/comments', methods=['GET', 'POST', 'OPTIONS'])
@require_active_login(['POST'])
def api_comments():
    if request.method == 'POST':
        post_data = json.loads(request.data)

        item = Item.query.filter_by(id=post_data['item']).first()

        if not item:
            return abort(404)

        user = User.query.filter_by(id=g.user.id).first()

        if not user:
            return abort(400)

        comment = Comment(item, user, post_data['comment'])
        db.session.add(comment)
        db.session.commit()

        emails = []

        for c in item.comments.all():
            emails.append(c.user.email)

        if item.site:
            emails.append(item.site.owner.email)

        emails = set(emails)

        app.logger.debug('Sending notification about {0} to {1}'.format(
            comment.text,
            ', '.join(emails)))

        for email in emails:
            # Send comment notification to users that posted on the page
            send_comment_notification(
                    email,
                    g.user,
                    comment,
                    item)

        app.logger.debug(request.data)

        return jsonify(status='OK', _allow_origin_cb=allow_all_origins)

    if not request.args.get('item_url'):
        return abort(400)

    item = get_or_add_item(
            request.args.get('item_url'),
            request.args.get('item_title'))

    return_data = {
            'item': item.as_dict(),
            'comments': [
                i.as_dict() for i in \
                        item.comments.order_by(
                            Comment.created.desc()).all()],
            'comment_count': item.comments.count()}

    if g.user:
        return_data.update({'logged_in_as': g.user.username})

    return jsonify(_allow_origin_cb=allow_all_origins,
            **return_data)


@app.route('/api/check-login')
def check_login():
    if g.user:
        return jsonify(status='OK', _allow_origin_cb=allow_all_origins)
    else:
        return jsonify(status=False, _allow_origin_cb=allow_all_origins)
