from sqlalchemy import Column, Integer, String, PickleType, ForeignKey
from sqlalchemy.orm import relationship

from .. import db


class Traceback(db.Model):

    __tablename__ = 'traceback'

    id = Column(Integer, primary_key=True)
    error_line = Column(String(), unique=False)
    error_line_number = Column(Integer, unique=False)
    file = Column(String(), unique=False)
    module = Column(String(), unique=False)
    module_line_number = Column(Integer, unique=False)
    local_vars = Column(PickleType(), unique=False)
    object_vars = Column(PickleType(), unique=False)
    custom_inspection = Column(PickleType(), unique=False)
    source_code = Column(String(), unique=False)

    crashreport_id = Column(Integer, ForeignKey('crashreport.id'))
    crashreport = relationship("CrashReport", back_populates="traceback")

    __mappings__ = {'Error Line': 'error_line',
                    'Error Line Number': 'error_line_number',
                    'File': 'file',
                    'Module': 'module',
                    'Module Line Number': 'module_line_number',
                    'Local Variables': 'local_vars',
                    'Object Variables': 'object_vars',
                    'Custom Inspection': 'custom_inspection',
                    'Source Code': 'source_code'}

    def __init__(self, **traceback_fields):
        for k, v in traceback_fields.iteritems():
            column = Traceback.__mappings__.get(k)
            if column:
                setattr(self, column, v)

    def __getitem__(self, item):
        return getattr(self, Traceback.__mappings__[item])