from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from .. import db


class Group(db.Model):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    name = Column(String(120), unique=True)
    description = Column(String, unique=False)
    uuids = relationship('UUID', uselist=True)
    applications = relationship('Application', uselist=True)
    join_requests_id = Column(Integer,  ForeignKey('users.id'))
    join_requests = relationship('User', uselist=True, foreign_keys=[join_requests_id])

    def __init__(self, name, description='', users=None):
        self.name = name
        self.description = description
        if users is not None:
            for user in users:
                self.users.append(user)

    def add_report(self, report):
        self.reports.append(report)
        self.uuids.append(report.uuid)