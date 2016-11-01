from sqlalchemy import Column, Integer, String

from .. import db


class Application(db.Model):
    __tablename__ = 'application'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    description = Column(String, unique=False)

    # Version info
    version_0 = Column(Integer)
    version_1 = Column(Integer)
    version_2 = Column(Integer)

    def __init__(self, name, version, description='', uuids=None):
        self.name = name
        self.description = description
        self.version_0, self.version_1, self.version_2 = map(int, version.split('.'))

        if uuids is not None:
            for uuid in uuids:
                self.uuids.append(uuid)

    @property
    def version_string(self):
        return '%d.%d.%d' % (self.version_0, self.version_1, self.version_2)