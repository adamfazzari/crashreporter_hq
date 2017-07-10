import re
import datetime
from models import CrashReport, Group, User, Traceback
from . import db

_report_cache = []
cr_number_regex = re.compile('crash_report_(\d+)\.json')


def delete_report(delete_similar=False, *numbers):
    if delete_similar:
        # Go through all the crash reports that are related and delete them and their traceback
        for group_id in db.session.query(CrashReport.related_group_id.distinct()).filter(CrashReport.id.in_(numbers)).all():
            query = db.session.query(CrashReport.id).filter(CrashReport.related_group_id == group_id[0])
            report_ids = zip(*query.all())[0]

            db.session.query(Traceback).filter(Traceback.crashreport_id.in_(report_ids)).delete(synchronize_session='fetch')
            query.delete(synchronize_session='fetch')

    else:
        query = CrashReport.query.filter(CrashReport.id.in_(numbers))
        query.delete(synchronize_session='fetch')

        query = Traceback.query.filter(Traceback.crashreport_id.in_(numbers))
        query.delete(synchronize_session='fetch')

    db.session.expire_all()
    db.session.commit()
    return len(CrashReport.query.filter(CrashReport.id.in_(numbers)).all()) == 0


def save_report(payload):
    params = payload.get('HQ Parameters')
    # Find the user associated with the API key and the group they belong to.
    # If that group exists, add the report to the group
    api_key = params.get('api_key', None)
    user = User.query.filter(User.api_key == api_key).first()
    if user is not None and user.group:
        # If the date comes in from the future (> 1 day), set the date to today's date
        crash_date = datetime.datetime.strptime(payload['Date'], '%d %B %Y')
        now = datetime.datetime.now()
        time_diff = (crash_date-now).total_seconds()
        if time_diff > 24 * 60 * 60:
            payload['Date'] = now.strftime('%d %B %Y')

        if not isinstance(payload['Application Version'], basestring):
            return None, "Application version must be a 3 decimal string. eg '2.1.0'"

        if not isinstance(payload['Application Name'], basestring):
            return None, 'Invalid application name %s' % payload['Application Name']

        # Check to see if this error is due to infinite recursion and if so
        # prune the list of tracebacks so the database doesn't get filled with redundant information
        if 'maximum recursion' in payload['Error Message']:
            # Prune the redundant tracebacks to save space
            repeated_traceback = payload['Traceback'][-1]['Module']
            max_redundancy = 5
            count = 0
            for tb in reversed(payload['Traceback']):
                if tb['Module'] == repeated_traceback:
                    count += 1
                    if count > max_redundancy:
                        payload['Traceback'].remove(tb)

        cr = CrashReport(user.group, **payload)


        cr.commit()

        return cr, 'Success'
    else:
        return None, 'Invalid or missing API Key.'

def get_all_reports():
    return CrashReport.query.all()


def create_user(email, password, **kwargs):
    """
    Create a new user, or return the existing user if email is not unique
    :param password:
    :param group:
    :param admin:
    :return:
    """
    u = User.query.filter(User.email == email).first()
    if not u:
        u = User(email, password, **kwargs)
        db.session.add(u)
        db.session.commit()

    return u


def create_group(name, users=None):

    g = Group.query.filter(Group.name == name).first()
    if not g:
        g = Group(name, users)
        db.session.add(g)
        db.session.commit()

    return g