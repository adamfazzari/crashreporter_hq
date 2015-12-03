__author__ = 'calvin'

from hq.database import init_db

init_db()


from hq.database import db_session
from hq.models import User


def create_user(email, password):
    u = User(email, password)

    all_users = User.query.all()
    userquery = User.query.filter(User.email == email).first()

    if not userquery:
        db_session.add(u)
        db_session.commit()

    print 'Registered users:'
    print ','.join([u.email for u in User.query.all()])


if __name__ == '__main__':

    create_user('calvin', 'sensoft')
    create_user('adam', 'sensoft2')
