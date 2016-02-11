
from flask import request, render_template, flash, redirect, url_for
import flask.ext.login as flask_login

from ..models import User

from .. import app



@app.route('/users', methods=['GET'])
@flask_login.login_required
def users():
    if request.method == 'GET':
        uid = int(request.args.get('id', -1))
        if uid and flask_login.current_user.id == uid:
            # Show profile for the logged in user
            return render_template('users.html', user_list=[flask_login.current_user], user=flask_login.current_user)
        elif uid < 0:
            if flask_login.current_user.admin:
                user_list = User.query.all()
                return render_template('users.html', user_list=user_list, user=flask_login.current_user)
            else:
                return 'User does not exist.'

        else:
            return 'Admin access only.'





