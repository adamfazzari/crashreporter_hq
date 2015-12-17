from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base
from datetime import datetime

from .traceback import Traceback
from sqlalchemy.orm import relationship


class CrashReport(Base):
    __tablename__ = 'crashreport'

    id = Column(Integer, primary_key=True)
    date = Column(DateTime())
    application_name = Column(String(50), unique=False)
    application_version = Column(Integer, unique=False)
    error_message = Column(String(), unique=False)
    error_type = Column(String(), unique=False)
    user_identifier = Column(String(100), unique=False)

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

    def __getitem__(self, item):
        return getattr(self, CrashReport.__mappings__[item])

CrashReport.traceback = relationship("Traceback", order_by=Traceback.id, back_populates="crashreport")