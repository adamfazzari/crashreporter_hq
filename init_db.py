__author__ = 'calvin'


from migrate.versioning import api
from crashreporter_hq.config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO
from crashreporter_hq import db

import os.path

db.create_all()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI, SQLALCHEMY_MIGRATE_REPO, api.version(SQLALCHEMY_MIGRATE_REPO))


from crashreporter_hq.tools import create_group, create_user


if __name__ == '__main__':

    grp = create_group('Sensoft')

    calvin = create_user('calvin@email.com', 'apple', name='Calvin', group=grp, admin=True, api_key='123456')
    print calvin.email, calvin.api_key
    adam = create_user('adam@email.com', 'banana', name='Adam', api_key='qwerty')
    print adam.email, adam.api_key

    asd=2


