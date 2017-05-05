from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
state = Table('state', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('state', VARCHAR),
    Column('name', VARCHAR(length=20)),
    Column('description', VARCHAR(length=150)),
    Column('uuid_id', INTEGER),
    Column('application_name', VARCHAR(length=50)),
    Column('application_version', INTEGER),
    Column('group_id', INTEGER),
)

state = Table('state', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('state', String),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('uuid_id', Integer),
    Column('application_id', Integer),
    Column('group_id', Integer),
)

statistic = Table('statistic', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('count', INTEGER),
    Column('name', VARCHAR(length=20)),
    Column('description', VARCHAR(length=150)),
    Column('uuid_id', INTEGER),
    Column('application_name', VARCHAR(length=50)),
    Column('application_version', INTEGER),
    Column('group_id', INTEGER),
)

statistic = Table('statistic', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('count', Integer, default=ColumnDefault(0)),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('uuid_id', Integer),
    Column('application_id', Integer),
    Column('group_id', Integer),
)

timer = Table('timer', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('count', INTEGER),
    Column('time', INTEGER),
    Column('name', VARCHAR(length=20)),
    Column('description', VARCHAR(length=150)),
    Column('uuid_id', INTEGER),
    Column('application_name', VARCHAR(length=50)),
    Column('application_version', INTEGER),
    Column('group_id', INTEGER),
)

timer = Table('timer', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('count', Integer, default=ColumnDefault(0)),
    Column('time', Integer),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('uuid_id', Integer),
    Column('application_id', Integer),
    Column('group_id', Integer),
)

sequence = Table('sequence', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('count', INTEGER),
    Column('name', VARCHAR(length=20)),
    Column('description', VARCHAR(length=150)),
    Column('uuid_id', INTEGER),
    Column('application_name', VARCHAR(length=50)),
    Column('application_version', INTEGER),
    Column('group_id', INTEGER),
)

sequence = Table('sequence', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('count', Integer, default=ColumnDefault(0)),
    Column('name', String(length=20)),
    Column('description', String(length=150)),
    Column('uuid_id', Integer),
    Column('application_id', Integer),
    Column('group_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['state'].columns['application_name'].drop()
    pre_meta.tables['state'].columns['application_version'].drop()
    post_meta.tables['state'].columns['application_id'].create()
    pre_meta.tables['statistic'].columns['application_name'].drop()
    pre_meta.tables['statistic'].columns['application_version'].drop()
    post_meta.tables['statistic'].columns['application_id'].create()
    pre_meta.tables['timer'].columns['application_name'].drop()
    pre_meta.tables['timer'].columns['application_version'].drop()
    post_meta.tables['timer'].columns['application_id'].create()
    pre_meta.tables['sequence'].columns['application_name'].drop()
    pre_meta.tables['sequence'].columns['application_version'].drop()
    post_meta.tables['sequence'].columns['application_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    pre_meta.tables['state'].columns['application_name'].create()
    pre_meta.tables['state'].columns['application_version'].create()
    post_meta.tables['state'].columns['application_id'].drop()
    pre_meta.tables['statistic'].columns['application_name'].create()
    pre_meta.tables['statistic'].columns['application_version'].create()
    post_meta.tables['statistic'].columns['application_id'].drop()
    pre_meta.tables['timer'].columns['application_name'].create()
    pre_meta.tables['timer'].columns['application_version'].create()
    post_meta.tables['timer'].columns['application_id'].drop()
    pre_meta.tables['sequence'].columns['application_name'].create()
    pre_meta.tables['sequence'].columns['application_version'].create()
    post_meta.tables['sequence'].columns['application_id'].drop()
