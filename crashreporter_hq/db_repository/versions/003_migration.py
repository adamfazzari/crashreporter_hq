from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
alias = Table('alias', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('alias', String(length=50), default=ColumnDefault('')),
    Column('user_identifier', String(length=100)),
    Column('user_id', Integer),
)

users = Table('users', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('name', VARCHAR(length=30)),
    Column('company', VARCHAR(length=50)),
    Column('email', VARCHAR(length=120)),
    Column('password', VARCHAR(length=50)),
    Column('admin', BOOLEAN),
    Column('api_key', VARCHAR(length=50)),
    Column('group_id', INTEGER),
    Column('group_admin', BOOLEAN),
    Column('alias_id', INTEGER),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['alias'].columns['user_id'].create()
    pre_meta.tables['users'].columns['alias_id'].drop()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['alias'].columns['user_id'].drop()
    pre_meta.tables['users'].columns['alias_id'].create()
