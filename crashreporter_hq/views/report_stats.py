from flask import Response
from sqlalchemy import func, asc

from groups import *
from ..models import CrashReport

import json


@app.route('/reports/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_report_stats():
    html = render_template('report_statistics.html', user=flask_login.current_user)
    return html


@app.route('/reports/get_stats', methods=['GET'])
def get_report_stats():
    if request.args.get('type') == 'date':
        q = db.session.query(CrashReport.date, func.count(CrashReport.date)).group_by(CrashReport.uuid_id).\
                               order_by(asc(CrashReport.date))
        data = [(d.year, d.month-1, d.day, d.hour, n) for d, n in q.all() if d.year == 2016]
    elif request.args.get('type') == 'user':
        q = db.session.query(CrashReport.uuid, func.count(CrashReport.uuid).label('# crashes')).\
            group_by(CrashReport.uuid)
        data = q.all()
    else:
        return 'Invalid request'
    json_response = json.dumps(data)
    response = Response(json_response, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(json_response))
    response.status_code = 200

    return response