from flask import Response
from sqlalchemy import func, asc

from groups import *
from ..models import CrashReport, Statistic, State, Timer, Sequence

import json

TRACKABLES = {'Statistic': Statistic, 'State': State, 'Timer': Timer, 'Sequence': Sequence}


@app.route('/usage/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_usage_stats():
    html = render_template('usage_stats2.html', user=flask_login.current_user)
    return html


@app.route('/usage/get_stats', methods=['GET'])
def get_usage_stats():

    q = Statistic.query.filter(Statistic.count is not None)
    q2 = db.session.query(State.state, func.count(State.id)).group_by(State.state)
    data = {'statistic': [(s.name, s.count) for s in q.all() if s.count],
            'state': [s for s in q2.all() if s is not s[0] is not None]}

    json_response = json.dumps(data)
    response = Response(json_response, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(json_response))
    response.status_code = 200
    return response


@app.route('/reports/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_report_stats():
    html = render_template('usage_stats.html', user=flask_login.current_user)
    return html


@app.route('/reports/get_stats', methods=['GET'])
def get_report_stats():
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

@app.route('/usagestats/upload', methods=['POST'])
def upload_stats():
    payload = json.loads(request.data)
    api_key = payload.get('API Key')

    if api_key is None:
        return 'Missing API Key.'
    user = User.query.filter(User.api_key == api_key).first()
    if user is None:
        return 'Upload failed'
    else:
        for trackable_name, data in payload.get('Data', {}).iteritems():
            cls = TRACKABLES.get(data['type'])
            trackable = cls.query.filter(cls.name==trackable_name, cls.group_id==user.group_id).first()
            if trackable is None:
                row = cls(trackable_name, payload['User Identifier'], payload['Application Name'], payload['Application Version'], user.group)
                db.session.add(row)
            else:
                if data['type'] == 'State':
                    trackable.state = data['data']
                else:
                    trackable.count = data['data']
        db.session.commit()

