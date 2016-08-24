from flask import Response
from sqlalchemy import func, asc
from datetime import datetime
from groups import *
from ..models import CrashReport, UUID

import json


@app.route('/reports/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_report_stats():
    html = render_template('report_statistics.html', user=flask_login.current_user)
    return html


@app.route('/reports/get_stats', methods=['GET'])
def get_report_stats():
    if request.args.get('type') == 'date':
        # Query for the number of reports for each day
        q = db.session.query(func.date(CrashReport.date), func.count(func.DATE(CrashReport.date)))
        # Only dates that are before today (so we take out units with time-stamps in the future)
        q = q.filter(CrashReport.date <= datetime.now())
        # Group / bin the results by day in ascending order
        q = q.group_by(func.date(CrashReport.date)).order_by(asc(CrashReport.date))

        # Because SQLite does not support the Date class in queries, we cannot cast the results
        # Instead, do the casting ourselves
        data = []
        for datestr, n in q.all():
            d = datetime.strptime(datestr, '%Y-%m-%d')
            data.append((d.year, d.month-1, d.day, d.hour, n))

    elif request.args.get('type') == 'user':
        # https://stackoverflow.com/questions/25500904/counting-relationships-in-sqlalchemy/25525771#25525771
        q = db.session.query(UUID.user_identifier, func.count(CrashReport.id)).join(UUID.reports).group_by(UUID.user_identifier)
        data = q.all()
    else:
        return 'Invalid request'
    json_response = json.dumps(data)
    response = Response(json_response, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(json_response))
    response.status_code = 200

    return response