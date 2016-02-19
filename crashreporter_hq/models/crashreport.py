from sqlalchemy import Column, Integer, String, DateTime, Table, ForeignKey, func
from datetime import datetime
from .. import db

from .traceback import Traceback
from sqlalchemy.orm import relationship


SimilarReports = Table("SimilarReports", db.metadata,
                       Column("related_to_id", Integer, ForeignKey("crashreport.id")),
                       Column("related_by_id", Integer, ForeignKey("crashreport.id")))


class CrashReport(db.Model):

    __tablename__ = 'crashreport'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime())
    application_name = Column(String(50), unique=False)
    application_version = Column(Integer, unique=False)
    error_message = Column(String(''), unique=False)
    error_type = Column(String(''), unique=False)
    user_identifier = Column(String(100), unique=False)
    related_group_id = Column(Integer, unique=False)
    related_reports = relationship("CrashReport",
                                   secondary=SimilarReports,
                                   primaryjoin=id==SimilarReports.c.related_to_id,
                                   secondaryjoin=id==SimilarReports.c.related_by_id)

    group_id = Column(Integer, ForeignKey('group.id'))
    group = relationship('Group', backref='reports', foreign_keys=[group_id])

    __mappings__ = {'Report Number': 'id',
                    'Application Name': 'application_name',
                    'Application Version': 'application_version',
                    'Error Message': 'error_message',
                    'Error Type': 'error_type',
                    'User': 'user_identifier',
                    'Traceback': 'traceback',
                    'Date': 'date'}

    def __init__(self, **report_fields):
        for k, v in report_fields.iteritems():
            column = CrashReport.__mappings__.get(k)
            if column and column != 'traceback':
                setattr(self, column, v)
        self.date = datetime.strptime("{Date} {Time}".format(**report_fields), '%d %B %Y %I:%M %p')

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

    def __getitem__(self, item):
        return getattr(self, CrashReport.__mappings__[item])

    def get_similar_reports(self):
        signature = tuple([(tb.module, tb.error_line_number) for tb in self.traceback])
        related_id = hash(signature)
        return CrashReport.query.filter(CrashReport.related_group_id == related_id).all()

    def __repr__(self):
        return "{s.id} {s.error_type}".format(s=self)

CrashReport.traceback = relationship("Traceback", order_by=Traceback.id, back_populates="crashreport")

