from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey
from datetime import datetime
from .. import db

from .traceback import Traceback
from uuid import UUID
from sqlalchemy.orm import relationship

from applications import Application

SimilarReports = Table("SimilarReports", db.metadata,
                       Column("related_to_id", Integer, ForeignKey("crashreport.id")),
                       Column("related_by_id", Integer, ForeignKey("crashreport.id")))


class CrashReport(db.Model):

    __tablename__ = 'crashreport'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime())
    application_id = Column(Integer, ForeignKey('application.id'))
    application = relationship('Application', backref='reports', foreign_keys=[application_id])
    error_message = Column(String(''), unique=False)
    error_type = Column(String(''), unique=False)
    uuid_id = Column(Integer, ForeignKey('uuid.id'), unique=False)
    uuid = relationship('UUID', backref='reports', foreign_keys=[uuid_id])
    related_group_id = Column(Integer, unique=False)
    related_reports = relationship("CrashReport",
                                   secondary=SimilarReports,
                                   primaryjoin=id==SimilarReports.c.related_to_id,
                                   secondaryjoin=id==SimilarReports.c.related_by_id)

    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='reports', foreign_keys=[group_id])

    __mappings__ = {'Report Number': 'id',
                    'Error Message': 'error_message',
                    'Error Type': 'error_type',
                    'User': 'uuid',
                    'Traceback': 'traceback',
                    'Date': 'date'}

    def __init__(self, **report_fields):
        version_0, version_1, version_2 = map(int, report_fields['Application Version'])

        application = Application.query().filter(Application.name == report_fields['Application Name'],
                                                 Application.version_0 == version_0,
                                                 Application.version_1 == version_1,
                                                 Application.version_2 == version_2).first()
        if application is None:
            application = Application(report_fields['Application Name'], report_fields['Application Version'])
        self.application = application
        self.error_message = report_fields['Error Message']
        self.error_type = report_fields['Error Type']
        self.date = datetime.strptime("{Date} {Time}".format(**report_fields), '%d %B %Y %I:%M %p')

        # Attach to a uuid, or create one if a report from this user has not been recieved before.
        existing_uuid = UUID.query.filter(UUID.user_identifier == report_fields['User']).first()
        if existing_uuid:
            self.uuid = existing_uuid
        else:
            self.uuid = UUID(report_fields['User'])

        self.application.uuids.append(self.uuid)

        for tb in report_fields['Traceback']:
            tb = Traceback(**tb)
            tb.crashreport = self

        similar_reports = self.get_similar_reports()
        if similar_reports:
            self.related_reports.extend(similar_reports)
            self.related_group_id = similar_reports[0].related_group_id
            for r in similar_reports:
                r.related_reports.append(self)
        else:
            signature = tuple([(tb.module, tb.error_line_number) for tb in self.traceback])
            related_id = hash(signature)
            self.related_group_id = related_id

        self.commit()

    def __getitem__(self, item):
        return getattr(self, CrashReport.__mappings__[item], '')

    def get_similar_reports(self):
        signature = tuple([(tb.module, tb.error_line_number) for tb in self.traceback])
        related_id = hash(signature)
        return CrashReport.query.filter(CrashReport.related_group_id == related_id).all()

    def __repr__(self):
        return "{s.id} {s.error_type}".format(s=self)

    def commit(self):
        db.session.add(self)
        db.session.add(self.uuid)
        for tb in self['Traceback']:
            db.session.add(tb)
        db.session.commit()

CrashReport.traceback = relationship("Traceback", order_by=Traceback.id, back_populates="crashreport")

