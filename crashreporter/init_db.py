__author__ = 'calvin'

from hq.database import init_db

init_db()


from hq.database import db_session
from hq.models import User, Group


def create_user(email, password, group=None, admin=False):
    u = User.query.filter(User.email == email).first()
    if not u:
        u = User(email, password, admin)
        db_session.add(u)
        db_session.commit()
    if group:
        u.group = group
    print 'Registered users:'
    print ','.join([u.email for u in User.query.all()])
    return u


def create_group(name, users=None):

    g = Group.query.filter(Group.name == name).first()
    if not g:
        g = Group(name, users)
        db_session.add(g)
        db_session.commit()

    print 'Registered users:'
    print ','.join([u.name for u in Group.query.all()])
    return g

if __name__ == '__main__':

    grp = create_group('Sensoft')

    calvin = create_user('calvin', 'sensoft', group=grp, admin=True)

    adam = create_user('adam', 'sensoft2')

    asd=3


