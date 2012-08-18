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

from desqus import app
from flask import render_template, flash, session, url_for, redirect, Markup, \
        request, json, abort

from desqus.forms import LoginForm, RegistrationForm, ItemForm
from desqus.db import db, User, Item, Comment
from desqus.tools.cors import jsonify


@app.route('/')
def index():
    return render_template('desqus/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        flash(u'Logged in as {0}'.format(form.user.username), 'info')
        session['user_id'] = form.user.id
        return form.redirect('index')

    return render_template('desqus/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(form.username.data, form.email.data, form.password.data)
        db.session.add(user)
        db.session.commit()

        session['user_id'] = user.id

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


@app.route('/api/comments', methods=['GET', 'POST'])
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

        return jsonify(status='OK')
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

        return jsonify(**return_data)


@app.route('/api/check-login')
def check_login():
    if session.get('user_id'):
        app.logger.debug('check-login: Logged in')
        return jsonify(status='OK')
    else:
        app.logger.debug('check-login: Not logged in')
        return jsonify(status=False)


@app.route('/logout')
def logout():
    del session['user_id']
    flash(u'You have been logged out.')
    return redirect(url_for('index'))
