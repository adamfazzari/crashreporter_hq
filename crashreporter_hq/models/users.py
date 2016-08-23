import uuid
import flask.ext.login as flask_login
from .. import login_manager

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .. import db


class Group(db.Model):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    description = Column(String, unique=False)
    uuid_id = Column(Integer,  ForeignKey('uuid.id'))
    uuids = relationship('UUID', uselist=True, foreign_keys=[uuid_id])
    join_requests_id = Column(Integer,  ForeignKey('users.id'))
    join_requests = relationship('User', uselist=True, foreign_keys=[join_requests_id])

    def __init__(self, name, description='', users=None):
        self.name = name
        self.description = description
        if users is not None:
            for user in users:
                if isinstance(user, User):
                    self.users.append(user)

    def add_report(self, report):
        if report not in self.reports:
            self.reports.append(report)
        if report.uuid not in self.uuids:
            self.uuids.append(report.uuid)


class Alias(db.Model):
    __tablename__ = 'alias'
    id = Column(Integer, primary_key=True)
    alias = Column(String(50), unique=False, default='')
    uuid_id = Column(Integer,  ForeignKey('uuid.id'))
    uuid = relationship('UUID', foreign_keys=[uuid_id])
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='aliases', foreign_keys=[group_id])

    def __init__(self, group, name, uuid):
        self.group = group
        self.alias = name
        self.uuid = uuid

    @property
    def user_identifier(self):
        return self.uuid.user_identifier


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
    # aliases = relationship('Alias', back_populates='user', uselist=True)

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
