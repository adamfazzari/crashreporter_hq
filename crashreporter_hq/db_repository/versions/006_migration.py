from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
traceback = Table('traceback', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('error_line', String),
    Column('error_line_number', Integer),
    Column('file', String),
    Column('module', String),
    Column('module_line_number', Integer),
    Column('local_vars', PickleType),
    Column('object_vars', PickleType),
    Column('custom_inspection', PickleType),
    Column('source_code', String),
    Column('crashreport_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['traceback'].columns['custom_inspection'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['traceback'].columns['custom_inspection'].drop()
