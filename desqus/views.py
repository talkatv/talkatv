from desqus import app
from flask import render_template, flash, session, url_for, redirect

from desqus.forms import LoginForm, RegistrationForm
from desqus.db import db, User


@app.route('/')
def index():
    return render_template('desqus/index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        flash(u'Logged in as {0}'.format(form.user.username))
        session['user_id'] = form.user.id
        return redirect(url_for('index'))

    return render_template('desqus/login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()

    if form.validate_on_submit():
        user = User(form.username.data, form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        session['user_id'] = user.id
        flash(u'Welcome, {0}!'.format(user.username))
        return redirect(url_for('index'))

    return render_template('desqus/register.html', form=form)


@app.route('/logout')
def logout():
    del session['user_id']
    flash(u'You have been logged out.')
    return redirect(url_for('index'))
