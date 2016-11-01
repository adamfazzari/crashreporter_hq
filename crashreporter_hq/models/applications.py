from sqlalchemy import Column, Integer, String, Boolean

from .. import db


class Application(db.Model):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    description = Column(String, unique=False)
    is_release = Column(Boolean)
    # Version info
    version_0 = Column(Integer)
    version_1 = Column(Integer)
    version_2 = Column(Integer)

    def __init__(self, name, version, description='', is_release=False, uuids=None):
        self.name = name
        self.description = description
        self.version_0, self.version_1, self.version_2 = map(int, version.split('.'))
        self.is_release = is_release

        if uuids is not None:
            for uuid in uuids:
                self.uuids.append(uuid)

    @property
    def version_string(self):
        return '%d.%d.%d' % (self.version_0, self.version_1, self.version_2)

    def __repr__(self):
        return '{s.name} - v{s.version_0}.{s.version_1}.{s.version_2}'.format(s=self)