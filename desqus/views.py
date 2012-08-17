from desqus import app
from flask import render_template, flash, session, url_for, redirect

from desqus.forms import LoginForm


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
