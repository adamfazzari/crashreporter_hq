
from flask import request, render_template, flash, redirect, url_for

import flask.ext.login as flask_login

from .. import app, db_session
from ..models import User
from ..forms import LoginForm, SignUpForm


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', title='Sign In', form=form)
    elif form.validate_on_submit():
        email = request.form['email']
        user = User.query.filter(User.email == email).first()
        if user:
            if request.form['password'] == user.password:
                flask_login.login_user(user)
                return redirect(request.args.get('next') or url_for('home'))
            else:
                flash('Incorrect password. Please try again.')
                return redirect(url_for('login'))
        else:
            return 'No user by the name of %s exists' % email

    else:
        return 'Bad login'

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()

    if request.method == 'GET':
        return render_template('signup.html', title='Sign Up', form=form)
    elif form.validate_on_submit():
        user = User.query.filter(User.email == form.data['email']).first()
        if user is None:
            u = User(admin=False, **form.data)
            db_session.add(u)
            db_session.commit()
            flash('Account under {email} has been created.'.format(**form.data))
            return redirect(url_for('login'))


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


