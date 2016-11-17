from __future__ import absolute_import

import flask.ext.login as flask_login
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

import uuid
from .group import Group
from .. import db
from .. import login_manager


class User(db.Model, flask_login.UserMixin):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String(30), unique=False, default='')
    company = Column(String(50), unique=False, default='')
    email = Column(String(120), unique=True)
    password = Column(String(50), unique=True)
    admin = Column(Boolean(False))
    api_key = Column(String(50), unique=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='users', foreign_keys=[group_id])
    group_admin = Column(Boolean, default=False)

    def __init__(self, email, password, name='', company='', admin=False, group=None, api_key=None, **kwargs):
        self.email = email
        self.password = password
        self.admin = admin
        self.name = name
        self.company = company
        if admin:
            self.group_admin = True
        if api_key is None:
            # Generate a new unique API key for the user.
            while 1:
                api_key = str(uuid.uuid4()).replace('-', '')
                if not User.query.filter(User.api_key == api_key).first():
                    self.api_key = api_key
                    break
        else:
            self.api_key = api_key

        # Add the groups this user belongs to
        if group:
            if isinstance(group, basestring):
                group = Group.query.filter(Group.name == group).first()
            group.users.append(self)

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
