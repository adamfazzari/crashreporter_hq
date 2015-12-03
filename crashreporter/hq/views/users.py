
from flask import request, render_template, flash, redirect, url_for
import flask.ext.login as flask_login

from ..models import User

from .. import app



@app.route('/users', methods=['GET'])
def users():

    if request.method == 'GET':
        query = User.query.all()
        user_list = [u.email for u in query]
        return render_template('users.html', user_list=user_list, user=flask_login.current_user.get_id())



