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

from flask import g, flash, request, url_for, redirect, render_template

from talkatv import app, db
from talkatv.decorators import require_active_login
from talkatv.forms import ProfileForm, ChangePasswordForm
from talkatv.models import OpenID, User


@app.route('/profile/edit', methods=['GET', 'POST'])
@require_active_login()
def edit_profile():
    '''
    Edit profile

    - Save profile data
    - Add OpenID
    '''
    form = ProfileForm()

    if form.validate_on_submit():
        openid = OpenID.query.filter_by(url=form.openid.data).first()

        if not openid and form.openid.data:
            openid = OpenID(g.user, form.openid.data)

        if form.username.data and not form.username.data == g.user.username:
            g.user.username = form.username.data
            flash('Your username has been changed to {0}'.format(
                form.username.data),
                    'info')

        if form.email.data and not form.email.data == g.user.email:
            g.user.email = form.email.data
            flash('Your email has been changed to {0}'.format(form.email.data), 'info')

        db.session.commit()
        return redirect(url_for('edit_profile'))

    else:
        form.username.data = request.args.get('username',
                getattr(g.user, 'username', form.username.data))
        form.email.data = request.args.get('email',
                getattr(g.user, 'email', form.email.data))

        if not g.user.openids.count():
            form.openid.data = request.args.get('openid', form.openid.data)
        else:
            form.openid.data = request.args.get('openid',
                g.user.openids.first().url)

    return render_template('talkatv/profile/edit.html', form=form)


@app.route('/profile/change-password', methods=['GET', 'POST'])
@require_active_login()
def change_password():
    form = ChangePasswordForm()

    if form.validate_on_submit():
        if g.user.password is None or \
                g.user.check_password(form.password.data):
            g.user.set_password(form.new_password.data)

            db.session.commit()

            flash('Your password has been changed!', 'success')
            return redirect(url_for('change_password'))

    return render_template('talkatv/profile/change-password.html', form=form)
