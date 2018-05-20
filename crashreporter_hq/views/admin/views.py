from crashreporter_hq.models import CrashReport, Application

from crashreporter_hq.views.users import *
from crashreporter_hq import db


@app.route('/admin/recompute_related_reports')
@flask_login.login_required
def recompute_related_reports():
    user = flask_login.current_user
    if user.admin:
        reports = CrashReport.query.all()
        for r in reports:
            r.related_group_id = None
            r.related_reports = []

        db.session.commit()

        for r in reports:
            r.related_group_id = CrashReport.get_related_hash(r)
            related_reports = r.get_similar_reports()
            r.related_reports.extend(related_reports)
            for related_report in related_reports:
                related_report.related_reports.append(r)
            db.session.commit()

        return 'done'