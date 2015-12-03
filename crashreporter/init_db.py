__author__ = 'calvin'

from hq.database import init_db

init_db()


from hq.database import db_session
from hq.models import User
u = User('admin', 'secret')
db_session.add(u)
db_session.commit()


asd = User.query.all()

qwe = User.query.filter(User.email == 'admin').first()

sdg456=7