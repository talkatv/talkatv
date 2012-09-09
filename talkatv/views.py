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

import os

from talkatv import app, oid, db

from flask import render_template, flash, session, url_for, redirect, \
        request, g

from talkatv.forms import LoginForm, RegistrationForm
from talkatv.models import User, Item, OpenID
from talkatv.tools.auth import set_active_user


@app.before_request
def lookup_current_user():
    g.user = None
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()

        if user is None:
            del session['user_id']
        else:
            set_active_user(user)


@app.route('/')
def index():
    return render_template('talkatv/index.html')


if 'SENTRY_PUBLIC_DSN' in app.config:
    from flask import Response

    @app.route('/talkatv.js')
    @app.route('/static/js/talkatv.js')
    def include_raven_js():
        # TODO this is an ugly solution.
        #zepto = open('extlib/zepto/zepto.js').read()
        jquery = open('extlib/jquery/jquery-1.8.1.js').read()
        raven = open('extlib/raven/raven-0.5.2.js').read()
        raven_config = 'Raven.config(\'{0}\');'.format(
                app.config['SENTRY_PUBLIC_DSN'])
        talkatv = open('extlib/talkatv-client/talkatv.js').read()

        response = Response('\n/* -- DIVIDER -- */\n'.join([
            jquery, raven, raven_config, talkatv]))
        response.mimetype = 'application/javascript'
        return response


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        flash(u'Logged in as {0}'.format(form.user.username), 'info')
        session['user_id'] = form.user.id
        return form.redirect('index')
    elif form.openid.data:
        return oid.try_login(form.openid.data, ask_for=['email', 'nickname'])

    return render_template('talkatv/login.html', form=form)


@oid.after_login
def openid_postlogin(resp):
    openid = OpenID.query.filter_by(url=resp.identity_url).first()

    if openid is not None:
        # Assume that an OpenID is always connected to a user
        user = openid.user

        flash(u'Welcome, {0}!'.format(user.username), 'info')

        set_active_user(user)

        return redirect(oid.get_next_url())

    registered_users = User.query.count()
    tmp_user_handle = 'user{0}'.format(registered_users + 1)

    user = User(tmp_user_handle,
           '{0}@localhost'.format(tmp_user_handle))
    openid = OpenID(user, resp.identity_url)

    db.session.add(user)
    db.session.add(openid)
    db.session.commit()

    flash(u'Please confirm your profile details', 'success')

    set_active_user(user)

    return redirect(url_for('edit_profile', next=oid.get_next_url(),
        username=resp.nickname,
        email=resp.email,
        openid=resp.identity_url))


@app.route('/register', methods=['GET', 'POST'])
def register():
    '''
    Regular user/password registration
    '''
    if g.user:
        return redirect(url_for('index'))

    form = RegistrationForm()

    form.username.data = request.args.get('username', form.username.data)
    form.email.data = request.args.get('email', form.email.data)

    if form.validate_on_submit():
        user = User(form.username.data, form.email.data, form.password.data)

        db.session.add(user)
        db.session.commit()

        set_active_user(user)

        flash(u'Welcome, {0}!'.format(user.username), 'success')

        return redirect(url_for('index'))

    return render_template('talkatv/register.html', form=form)


@app.route('/item/list')
@app.route('/item/list/page/<int:page>')
def item_list(page=1):
    page = Item.query.order_by(Item.created.desc()).paginate(
            page,
            app.config.get('ITEMS_PER_PAGE', 20))

    return render_template('talkatv/item-list.html', items_page=page)


@app.route('/logout')
def logout():
    del session['user_id']
    flash(u'You have been logged out.')
    return redirect(url_for('index'))
