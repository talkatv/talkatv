# desqus - Commenting backend for static pages
# Copyright (C) 2012  desqus contributors, see AUTHORS
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

from desqus import app, oid, db

from flask import render_template, flash, session, url_for, redirect, Markup, \
        request, json, abort, g

from desqus.forms import LoginForm, RegistrationForm, ItemForm
from desqus.models import User, Item, Comment, OpenID
from desqus.tools.cors import jsonify, allow_all_origins
from desqus.decorators  import require_active_login


@app.before_request
def lookup_current_user():
    g.user = None
    if 'user_id' in session:
        user = User.query.filter_by(id=session['user_id']).first()

        if user is None:
            del session['user_id']

        g.user = user


@app.route('/')
def index():
    return render_template('desqus/index.html')


@app.route('/login', methods=['GET', 'POST'])
@oid.loginhandler
def login():
    if g.user is not None:
        app.logger.debug('g.user is not None, redirecting to {0}'.format(
            oid.get_next_url()))
        return redirect(url_for('index'))

    form = LoginForm()

    if form.validate_on_submit():
        flash(u'Logged in as {0}'.format(form.user.username), 'info')
        session['user_id'] = form.user.id
        return form.redirect('index')
    elif form.openid.data:
        return oid.try_login(form.openid.data, ask_for=['email', 'nickname'])

    return render_template('desqus/login.html', form=form)


@oid.after_login
def openid_postlogin(resp):
    openid = OpenID.query.filter_by(url=resp.identity_url).first()

    if openid is not None:
        # Assume that an OpenID is always connected to a user
        user = openid.user

        flash(u'Welcome, {0}!'.format(user.username), 'info')

        session['user_id'] = user.id
        g.user = user

        return redirect(oid.get_next_url())

    flash(u'Please confirm your profile details', 'success')

    return redirect(url_for('register', next=oid.get_next_url(),
        username=resp.nickname,
        email=resp.email,
        openid=resp.identity_url))


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    form.username.data = request.args.get('username', form.username.data)
    form.email.data = request.args.get('email', form.email.data)
    form.openid.data = request.args.get('openid', form.openid.data)

    if form.validate_on_submit():
        user = User(form.username.data, form.email.data, form.password.data)

        openid = OpenID(user, form.openid.data)
        db.session.add(user)
        db.session.add(openid)
        db.session.commit()

        session['user_id'] = user.id
        g.user = user

        flash(u'Welcome, {0}!'.format(user.username), 'success')

        return redirect(url_for('index'))

    return render_template('desqus/register.html', form=form)


@app.route('/item', methods=['GET', 'POST'])
@app.route('/item/<int:item_id>')
def item(item_id=None):
    if not item_id:
        form = ItemForm()

        if form.validate_on_submit():
            user = User.query.filter_by(id=session['user_id']).first()
            item = Item(user, form.title.data, form.url.data)
            db.session.add(item)
            db.session.commit()

            flash(Markup('Item <a href="%s">%s</a> has been created!') %
                (item.url, item.title),
                'success')

        return render_template('desqus/item/form.html', form=form)


@app.route('/item/list')
def item_list():
    items = Item.query.all()

    return render_template('desqus/item-list.html', items=items)


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
    else:
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
