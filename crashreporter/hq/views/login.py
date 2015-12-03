
from flask import request, render_template, flash, redirect, url_for
from ..models import User
import flask.ext.login as flask_login

from .. import app
from ..models import User
from ..forms import LoginForm


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if request.method == 'GET':
        return render_template('login.html', title='Sign In', form=form)
    elif form.validate_on_submit():
        email = request.form['email']
        # user = users.get(email)
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


@app.route('/protected')
@flask_login.login_required
def protected():
    return 'Logged in as: ' + flask_login.current_user.id


@app.route('/logout')
def logout():
    flask_login.logout_user()
    flash('You have been logged out.')
    return redirect(url_for('login'))


