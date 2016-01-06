import re

from models import CrashReport, Group, User
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
    params = payload.get('HQ Parameters')
    # Find the user associated with the API key and the group they belong to.
    # If that group exists, add the report to the group
    api_key = params.get('api_key', None)
    user = User.query.filter(User.api_key == api_key).first()
    if user is not None:
        cr = CrashReport(**payload)
        if user.group:
            user.group.reports.append(cr)

        db_session.add(cr)
        for tb in cr['Traceback']:
            db_session.add(tb)
        db_session.commit()

        return cr, 'Success'
    else:
        return None, 'Invalid or missing API Key.'




def get_similar_reports(return_query=False):
    q = CrashReport.query.group_by('related_group_id')
    if return_query:
        return q
    else:
        return q.all()


def get_all_reports():
    return CrashReport.query.all()