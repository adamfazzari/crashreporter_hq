from flask import redirect, flash
import flask.ext.login as flask_login
from .. import users
from .. import login_manager

from sqlalchemy import Column, Integer, String
from ..database import Base

# class User(flask_login.UserMixin):
#     pass

class User(Base, flask_login.UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(50), unique=True)

    def __init__(self, email, password):
        self.email = email
        self.password = password

    def get_id(self):
        return self.email

    def __repr__(self):
        return '<User %r>' % (self.email)


@login_manager.user_loader
def user_loader(email):
    user = User.query.filter(User.email == email).first()
    if not user:
        return

    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    user = User.query.filter(User.email == email).first()
    if not user:
        return

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == user.password

    return user


# @login_manager.unauthorized_handler
# def unauthorized_handler():
#     return 'Unauthorized'