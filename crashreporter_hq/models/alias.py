from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .. import db


class Alias(db.Model):
    __tablename__ = 'alias'
    id = Column(Integer, primary_key=True)
    alias = Column(String(50), unique=False, default='')
    uuid_id = Column(Integer,  ForeignKey('uuid.id'))
    uuid = relationship('UUID', foreign_keys=[uuid_id])
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='aliases', foreign_keys=[group_id])

    def __init__(self, group, name, uuid):
        self.group = group
        self.alias = name
        self.uuid = uuid

    @property
    def user_identifier(self):
        return self.uuid.user_identifier
