import re

from models import CrashReport
from database import db_session

_report_cache = []
cr_number_regex = re.compile('crash_report_(\d+)\.json')


def delete_report(number):
    query = CrashReport.query.filter(CrashReport.id == number)
    cr = query.first()
    if cr:
        query.delete()
        db_session.commit()
    return len(CrashReport.query.filter(CrashReport.id == number).all()) == 0


def save_report(payload):
    cr = CrashReport(**payload)
    db_session.add(cr)
    for tb in cr['Traceback']:
        db_session.add(tb)
    db_session.commit()
    return cr


def get_similar_reports():
    return CrashReport.query.group_by('related_group_id').all()

def get_all_reports():
    return CrashReport.query.all()