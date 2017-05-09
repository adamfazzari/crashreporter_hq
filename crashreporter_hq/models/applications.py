from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from .. import db


class Application(db.Model):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    description = Column(String, unique=False)
    is_release = Column(Boolean)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', foreign_keys=[group_id])
    # Version info
    version_0 = Column(Integer)
    version_1 = Column(Integer)
    version_2 = Column(Integer)

    def __init__(self, name, version, group, description='', is_release=False):
        self.name = name
        self.description = description
        self.group = group
        self.version_0, self.version_1, self.version_2 = map(int, version)
        self.is_release = is_release

    @property
    def version_string(self):
        return '%d.%d.%d' % (self.version_0, self.version_1, self.version_2)

    def __repr__(self):
        return '{s.name} - v{s.version_0}.{s.version_1}.{s.version_2}'.format(s=self)