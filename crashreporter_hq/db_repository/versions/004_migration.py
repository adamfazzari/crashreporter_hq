from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
alias = Table('alias', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('alias', VARCHAR(length=50)),
    Column('user_identifier', VARCHAR(length=100)),
    Column('user_id', INTEGER),
)

alias = Table('alias', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('alias', String(length=50), default=ColumnDefault('')),
    Column('user_identifier', String(length=100)),
    Column('group_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['alias'].columns['user_id'].drop()
    post_meta.tables['alias'].columns['group_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['alias'].columns['user_id'].create()
    post_meta.tables['alias'].columns['group_id'].drop()
