import datetime

from flask_mail import Message
from celery import Celery

from sqlalchemy import func
from users import *

from ..models import CrashReport, Application
from .. import db, app, mail


celery = Celery('crashreporter_hq', broker='redis://localhost:6379/0')


@app.route('/start_task', methods=['GET'])
@flask_login.login_required
def start_task():
    task = send_status_report.apply_async(countdown=5)
    return 'Done'


@celery.task(name='tasks.send_status_report')
def send_status_report():
    with app.app_context():
        now = datetime.datetime.now()
        date = now - datetime.timedelta(days=7, hours=now.hour, minutes=now.minute, seconds=now.second)

        # Get the latest applications that have been released
        latest_applications = db.session.query(func.max(Application.version_0),
                                               func.max(Application.version_1),
                                               func.max(Application.version_2)) \
            .filter(Application.is_release == True) \
            .group_by(Application.name).all()

        top_reports = {}
        for v0, v1, v2 in latest_applications:
            r = db.session.query(CrashReport, func.count(CrashReport.id.distinct()),
                                 func.count(CrashReport.uuid_id.distinct()).label('total')) \
                .group_by(CrashReport.related_group_id) \
                .filter(CrashReport.date >= date, Application.is_release == True,
                        CrashReport.application.has(version_0=v0, version_1=v1, version_2=v2)) \
                .order_by('total DESC').all()
            if r:
                top_reports[r[0][0].application.name] = r
                group = r[0][0].group

        aliases = {a.user_identifier: a.alias for a in group.aliases}
        html = render_template('weekly_report.html', top_reports=top_reports, aliases=aliases)

        msg = Message('Hello from Flask',
                      html=html,
                      recipients=['test.sensoft@gmail.com'])

        mail.send(msg)

        return 'Success! Message sent'

