
from flask import request, render_template, flash, redirect, url_for
import flask.ext.login as flask_login

from ..models import User

from .. import app



@app.route('/users', methods=['GET'])
@flask_login.login_required
def users():

    if request.method == 'GET':
        if flask_login.current_user.admin:
            user_list = User.query.all()
            return render_template('users.html', user_list=user_list, user=flask_login.current_user)
        else:
            return 'Admin access only.'




