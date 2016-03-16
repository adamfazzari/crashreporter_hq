from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
sequence = Table('sequence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('count', Integer, default=ColumnDefault(0)),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('user_identifier', String(length=100)),
    Column('application_name', String(length=50)),
    Column('application_version', Integer),
    Column('group_id', Integer),
)

state = Table('state', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('state', String),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('user_identifier', String(length=100)),
    Column('application_name', String(length=50)),
    Column('application_version', Integer),
    Column('group_id', Integer),
)

statistic = Table('statistic', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('count', Integer, default=ColumnDefault(0)),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('user_identifier', String(length=100)),
    Column('application_name', String(length=50)),
    Column('application_version', Integer),
    Column('group_id', Integer),
)

timer = Table('timer', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('count', Integer, default=ColumnDefault(0)),
    Column('time', Integer),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('user_identifier', String(length=100)),
    Column('application_name', String(length=50)),
    Column('application_version', Integer),
    Column('group_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['sequence'].create()
    post_meta.tables['state'].create()
    post_meta.tables['statistic'].create()
    post_meta.tables['timer'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['sequence'].drop()
    post_meta.tables['state'].drop()
    post_meta.tables['statistic'].drop()
    post_meta.tables['timer'].drop()
