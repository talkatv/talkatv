from desqus import app
from flask import render_template, flash, session, url_for, redirect, Markup

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


@app.route('/api/comments')
def api_comments():
    comment_data = {'foo': 'bar'}

    user = User.query.filter_by(id=session.get('user_id')).first()
    if user:
        comment_data.update({'logged_in_as': user.username})

    app.logger.debug(comment_data)

    return jsonify(**comment_data)


@app.route('/logout')
def logout():
    del session['user_id']
    flash(u'You have been logged out.')
    return redirect(url_for('index'))
