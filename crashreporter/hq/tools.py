
import json
import glob
import re

from collections import OrderedDict

from config import *
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


def get_reports():
    return CrashReport.query.all()