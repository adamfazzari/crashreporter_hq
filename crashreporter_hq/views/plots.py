from flask import Response
from sqlalchemy import func, asc

from groups import *
from ..models import CrashReport

import json


@app.route('/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_stats():
    html = render_template('usage_stats.html', user=flask_login.current_user)
    return html


@app.route('/get_stats', methods=['GET'])
def get_stats():
    q = db.session.query(CrashReport.date, func.count(CrashReport.date)).group_by(CrashReport.user_identifier).\
                           order_by(asc(CrashReport.date))
    q2 = db.session.query(CrashReport.user_identifier, func.count(CrashReport.user_identifier).label('# crashes')).\
        group_by(CrashReport.user_identifier)
    data = {'date_data': [(d.year, d.month-1, d.day, d.hour, n) for d, n in q.all() if d.year == 2016],
            'user_data': q2.all()}

    json_response = json.dumps(data)
    response = Response(json_response, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(json_response))
    response.status_code = 200
    return response
