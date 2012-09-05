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

import smtplib

from email.mime.text import MIMEText

from talkatv import app


def get_smtp_connection():
    '''
    Returns an `sptmlib.SMTP` or `smptlib.SMTP_SSL` instance.

    Uses the app config:

    - ``SMTP_SSL``: ``True`` or ``False``. Defaults to ``False``
    - ``SMTP_HOST``: Remote host. Defaults to ``localhost``
    - ``SMTP_PORT``: Remote port. Defaults to ``25`` for non-SSL connections and
        ``465`` for SSL connections
    - ``SMTP_USER``: SMTP username. Defaults to `None`
    - ``SMTP_PASS``: SMTP password. Defaults to `None`
    '''
    if app.config['SMTP_SSL']:
        server = smtplib.SMTP_SSL(
                app.config['SMTP_HOST'] or 'localhost',
                app.config['SMTP_PORT'] or 465)
    else:
        server = smtplib.SMTP(
                app.config['SMTP_HOST'] or 'localhost',
                app.config['SMTP_PORT'] or 25)

    if app.config['SMTP_USER'] or app.config['SMTP_PASS']:
        server.login(app.config['SMTP_USER'], app.config['SMTP_PASS'])

    return server


SERVER = get_smtp_connection()


def send_mail(from_addr, to_addrs, subject, body):
    '''
    Send an email via the :py:data:`SERVER` SMTP connection.

    :param string from_addr: From: address
    :param list to_addrs: destination addresses
    :param string subject: message subject
    :param string body: message body
    :rtype: SMTP.sendmail() return data
    '''
    message = MIMEText(body.encode('utf-8'), 'plain', 'utf-8')
    message['From'] = from_addr
    message['To'] = ', '.join(to_addrs)
    message['Subject'] = subject.encode('utf-8')

    return SERVER.sendmail(from_addr, to_addrs, message.as_string())


def send_comment_notification(email, user, comment, item):
    mail_result = send_mail(
            app.config['NOTIFICATION_ADDR'],
            [email],
            '{0} commented on {1}'.format(
                user.username,
                item.title),
            '{user} commented on {title}:\n\n\t{text}\
            \n\nto see the comment, go to \n\n\t{url}'.format(
                user=user.username,
                title=item.title,
                url=item.url,
                text=comment.text))

    if mail_result is None:
        app.logger.error('{0} couldn\'t send mail: {1}'.format(
                email,
                mail_result))
    else:
        app.logger.error('{0} comment nofication send result: {1}'.format(
            email,
            mail_result))
