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

from flask import g, abort

from talkatv import app, db
from talkatv.models import Comment
from talkatv.notification import send_comment_notification


def post_comment(item, comment_data, user):
    comment_args = [item, g.user, comment_data['comment']]

    if 'reply_to' in comment_data:
        reply_to = Comment.query.filter(Comment.item == item)\
                .filter(Comment.id == comment_data['reply_to'])\
                .first()

        if not reply_to:
            app.logger.error('Invalid reply_to field: {0}'.format({
                'user': g.user.id,
                'comment_data': comment_data,
                'item': item.as_dict()}))

            abort(400)
        else:
            comment_args.append(reply_to)

    comment = Comment(*comment_args)
    db.session.add(comment)
    db.session.commit()

    emails = []

    if comment.reply_to:
        emails.append(comment.reply_to.user.email)

    if item.site:
        emails.append(item.site.owner.email)

    emails = set(emails)

    if emails:
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

    return comment


def get_context(item):
    '''
    Returns item and comment data in a JSON serializable format.
    '''
    comments = item.comments.filter(Comment.reply_to == None)\
            .order_by(Comment.created.desc())

    comments_data = []

    for comment in comments.all():
        comment_dict = comment.as_dict()
        comments_data.append(comment_dict)

        if comment.replies.count():
            traverse_comments(comment_dict, comment.replies.all())

    context_data = {
            'item': item.as_dict(),
            'comments': comments_data,
            'comment_count': comments.count()}

    if g.user:
        context_data.update({'logged_in_as': g.user.username})

    return context_data


def traverse_comments(parent_dict, replies):
    '''
    Iterate down a hirearchy of comment replies, the populate the parent_dict
    with the data found.

    Example:
    >>> comment = Comment.query.first()
    >>> comment_data = comment.as_dict()
    >>> traverse_comments(commend_data, comment.replies.all())
    >>> comment_data
    {'created': '2012-09-09T15:08:06.193223',
    'id': 58,
    'item': 29,
    'replies': [{'created': '2012-09-09T15:09:40.084748',
        'id': 59,
        'item': 29,
        'reply_to': 58,
        'text': u'Yep, working :)',
        'user_id': 1,
        'username': u'joar'}],
    'reply_to': None,
    'text': u'And remove the old comments!',
    'user_id': 1,
    'username': u'joar'}
    '''
    if replies:
        replies_data = []
        parent_dict.update({'replies': replies_data})
        for comment in replies:
            comment_dict = comment.as_dict()
            replies_data.append(comment_dict)
            replies = comment.replies.order_by(Comment.created.desc()).all()
            if len(replies):
                traverse_comments(comment_dict, replies)
