import flask.ext.login as flask_login
from .. import login_manager

from sqlalchemy import Column, Integer, String, Boolean
from ..database import Base


class User(Base, flask_login.UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    email = Column(String(120), unique=True)
    password = Column(String(50), unique=True)
    admin = Column(Boolean(False))

    def __init__(self, email, password, admin=False):
        self.email = email
        self.password = password
        self.admin = admin

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
