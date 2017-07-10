import re

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from itertools import izip_longest

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

    version_regex = re.compile("(\d+)[\s\.A-z]*(\d+)[\s\.A-z]*(?:(\d+)[\s\.A-z]*)?")

    def __init__(self, name, version, group, description='', is_release=False):
        self.name = name
        self.description = description
        self.group = group
        self.version_0, self.version_1, self.version_2 = map(int, version)
        self.is_release = is_release

    @property
    def version_string(self):
        return '%d.%d.%d' % (self.version_0, self.version_1, self.version_2)

    @staticmethod
    def parse_version_string(version_string):
        app_version_parse = re.findall(Application.version_regex, version_string)
        app_version = [a or b for (a, b) in izip_longest(app_version_parse[0], ('0', '0', '0'))]
        return app_version

    @staticmethod
    def get_application(name, version_string):
        # Parse the application version into a tuple
        app_version = Application.parse_version_string(version_string)
        q = Application.query.filter(Application.name == name)
        for ii, v in enumerate(app_version):
            q = q.filter(getattr(Application, 'version_%d' % ii) == int(v))
        application = q.first()
        return application

    def __repr__(self):
        return '{s.name} - v{s.version_0}.{s.version_1}.{s.version_2}'.format(s=self)