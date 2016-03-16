
from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from .. import db


__all__ = ['Statistic', 'State', 'Timer', 'Sequence']



class TrackableBase(object):
    '''
    Base class for trackables. Each row represents a trackable for a particular user and application
    '''
    def __init__(self, name, user_identifier, application_name, application_version, group):
        super(TrackableBase, self).__init__()
        self.name = name
        self.user_identifier = user_identifier
        self.application_name = application_name
        self.application_version = application_version
        self.group_id = group.id
        self.group = group
        getattr(self.group, self.__class__.__name__.lower()).append(self)


class Statistic(TrackableBase, db.Model):
    __tablename__ = 'statistic'
    __mapper_args__ = {'polymorphic_identity':'statistic','concrete': True}
    id = Column(Integer, primary_key=True)
    count = Column(Integer, default=0, unique=False)
    name = Column(String(20), unique=False)
    description = Column(String(150), unique=False)
    user_identifier = Column(String(100), unique=False)
    application_name = Column(String(50), unique=False)
    application_version = Column(Integer, unique=False)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='statistic', foreign_keys=[group_id])
    UniqueConstraint('group_id', 'name', 'user_identified', 'application_name', 'application_version')

    def __repr__(self):
        return '%s = %s' % (self.name, self.count)


class State(TrackableBase, db.Model):
    __tablename__ = 'state'
    __mapper_args__ = {'polymorphic_identity':'state', 'concrete': True}
    id = Column(Integer, primary_key=True)
    state = Column(String, unique=False)
    name = Column(String(20), unique=False)
    description = Column(String(150), unique=False)
    user_identifier = Column(String(100), unique=False)
    application_name = Column(String(50), unique=False)
    application_version = Column(Integer, unique=False)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='state', foreign_keys=[group_id])
    UniqueConstraint('group_id', 'name', 'user_identified', 'application_name', 'application_version')

    def __repr__(self):
        return '%s = %s' % (self.name, self.state)


class Timer(TrackableBase, db.Model):
    __tablename__ = 'timer'
    __mapper_args__ = {'polymorphic_identity':'timer', 'concrete': True}
    id = Column(Integer, primary_key=True)
    count = Column(Integer, default=0, unique=False)
    time = Column(Integer, unique=False)
    name = Column(String(20), unique=False)
    description = Column(String(150), unique=False)
    user_identifier = Column(String(100), unique=False)
    application_name = Column(String(50), unique=False)
    application_version = Column(Integer, unique=False)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='timer', foreign_keys=[group_id])
    UniqueConstraint('group_id', 'name', 'user_identified', 'application_name', 'application_version')

    def __repr__(self):
        return '%s = %d seconds' % (self.name, self.count)


class Sequence(TrackableBase, db.Model):
    __tablename__ = 'sequence'
    __mapper_args__ = {'polymorphic_identity':'sequence', 'concrete': True}
    id = Column(Integer, primary_key=True)
    count = Column(Integer, default=0, unique=False)
    name = Column(String(20), unique=False)
    description = Column(String(150), unique=False)
    user_identifier = Column(String(100), unique=False)
    application_name = Column(String(50), unique=False)
    application_version = Column(Integer, unique=False)
    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='sequence', foreign_keys=[group_id])
    UniqueConstraint('group_id', 'name', 'user_identified', 'application_name', 'application_version')

    def __repr__(self):
        return '%s = %s' % (self.name, self.count)