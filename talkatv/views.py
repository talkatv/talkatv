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

from talkatv import app, oid, db

from flask import render_template, flash, session, url_for, redirect, \
        request, json, abort, g

from talkatv.forms import LoginForm, RegistrationForm, ProfileForm
from talkatv.models import User, Item, Comment, OpenID
from talkatv.tools.cors import jsonify, allow_all_origins
from talkatv.tools.auth import set_active_user
from talkatv.decorators import require_active_login


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

        app.logger.debug(g.user)

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


@app.route('/api/comments', methods=['GET', 'POST', 'OPTIONS'])
@require_active_login(['POST'])
def api_comments():
    if request.method == 'POST':
        post_data = json.loads(request.data)

        item = Item.query.filter_by(id=post_data['item']).first()

        if not item:
            return abort(404)

        user = User.query.filter_by(id=session['user_id']).first()

        if not user:
            return abort(400)

        comment = Comment(item, user, post_data['comment'])
        db.session.add(comment)
        db.session.commit()

        app.logger.debug(request.data)

        return jsonify(status='OK', _allow_origin_cb=allow_all_origins)

    item = Item.query.filter_by(url=request.args.get('item_url')).first()

    if not item:
        title = request.args.get('item_title')
        url = request.args.get('item_url')

        item = Item(url, title)
        db.session.add(item)
        db.session.commit()

    return_data = {
            'item': item.as_dict(),
            'comments': [i.as_dict() for i in item.comments.all()]}

    user = User.query.filter_by(id=session.get('user_id')).first()
    if user:
        return_data.update({'logged_in_as': user.username})

    app.logger.debug(return_data)

    return jsonify(_allow_origin_cb=allow_all_origins,
            **return_data)


@app.route('/api/check-login')
def check_login():
    if session.get('user_id'):
        return jsonify(status='OK', _allow_origin_cb=allow_all_origins)
    else:
        return jsonify(status=False, _allow_origin_cb=allow_all_origins)


@app.route('/logout')
def logout():
    del session['user_id']
    flash(u'You have been logged out.')
    return redirect(url_for('index'))
