from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
application = Table('application', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('name', String(length=120)),
    Column('description', String),
    Column('version_0', Integer),
    Column('version_1', Integer),
    Column('version_2', Integer),
)

crashreport = Table('crashreport', pre_meta,
    Column('id', INTEGER, primary_key=True, nullable=False),
    Column('date', DATETIME),
    Column('application_name', VARCHAR(length=50)),
    Column('application_version', INTEGER),
    Column('error_message', VARCHAR),
    Column('error_type', VARCHAR),
    Column('uuid_id', INTEGER),
    Column('related_group_id', INTEGER),
    Column('group_id', INTEGER),
)

crashreport = Table('crashreport', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('date', DateTime),
    Column('application_id', Integer),
    Column('error_message', String(length='')),
    Column('error_type', String(length='')),
    Column('uuid_id', Integer),
    Column('related_group_id', Integer),
    Column('group_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['application'].create()
    pre_meta.tables['crashreport'].columns['application_name'].drop()
    pre_meta.tables['crashreport'].columns['application_version'].drop()
    post_meta.tables['crashreport'].columns['application_id'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['application'].drop()
    pre_meta.tables['crashreport'].columns['application_name'].create()
    pre_meta.tables['crashreport'].columns['application_version'].create()
    post_meta.tables['crashreport'].columns['application_id'].drop()


asd=3

sdfds=3