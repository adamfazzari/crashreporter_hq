from sqlalchemy import Column, Integer, String, ForeignKey, Boolean
from sqlalchemy.orm import relationship

from .. import db


class UUID(db.Model):

    __tablename__ = 'uuid'

    id = Column(Integer, primary_key=True)
    user_identifier = Column(String(100), unique=True)
    crashreport_black_listed = Column(Boolean(False), default=False)
    usagestats_black_listed = Column(Boolean(False), default=False)
    alias = relationship('Alias', back_populates='uuid', uselist=True)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', uselist=True, foreign_keys=[group_id])

    def __init__(self, user_identifier):
        self.user_identifier = user_identifier

    def __repr__(self):
        return "%d. %s" % (self.id, self.user_identifier)
