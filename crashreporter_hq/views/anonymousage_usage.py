from flask import Response
from sqlalchemy import func

from groups import *
from ..models import Statistic, State, Timer, Sequence

import json

TRACKABLES = {'Statistic': Statistic, 'State': State, 'Timer': Timer, 'Sequence': Sequence}


@app.route('/usage/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_usage_stats():
    state_trackables = [q.name for q in db.session.query(State.name.distinct().label('name'))]
    html = render_template('anonymous_usage.html', user=flask_login.current_user, states=state_trackables)
    return html


@app.route('/usage/get_stats', methods=['GET'])
def get_usage_stats():
    if request.args.get('type') == 'statistics':
        data = db.session.query(Statistic.name, func.sum(Statistic.count)).group_by(Statistic.name).all()
    elif request.args.get('type') == 'states':
        if request.args.get('name'):
            data = {'name': request.args.get('name'),
                    'counts': db.session.query(State.state, func.count(State.id)).
                                       filter(State.name==request.args.get('name')).
                                       group_by(State.state).all()
                    }
        else:
            data = [q.name for q in db.session.query(State.name.distinct().label('name'))]

    else:
        return 'Invalid query.'
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
    elif user.group is None:
        return 'User does not belong to a group.'
    else:
        for trackable_name, data in payload.get('Data', {}).iteritems():
            cls = TRACKABLES.get(data['type'])
            trackable = cls.query.filter(cls.name==trackable_name, cls.user_identifier==payload['User Identifier'], cls.group_id==user.group_id).first()
            if trackable is None:
                trackable = cls(trackable_name, payload['User Identifier'], payload['Application Name'], payload['Application Version'], user.group)
                db.session.add(trackable)
            # Apply the value of the data to the row
            if data['type'] == 'State':
                trackable.state = data['data']
            else:
                trackable.count = data['data']
        db.session.commit()

