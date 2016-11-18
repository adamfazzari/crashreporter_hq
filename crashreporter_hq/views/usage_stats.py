import json

import flask
from flask import Response
from sqlalchemy.orm import aliased

from constants import *
from groups import *
from ..models import Statistic, State, Timer, Sequence, UUID, StatisticBarPlot

TRACKABLES = {'Statistic': Statistic, 'State': State, 'Timer': Timer, 'Sequence': Sequence}


@app.route('/usage/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_usage_stats():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    state_trackables = [q.name for q in db.session.query(State.name.distinct().label('name'))]
    statistic_trackables = [t for t in db.session.query(StatisticBarPlot.id, StatisticBarPlot.name)\
                                                 .filter(StatisticBarPlot.group_id==group.id).all()]
    html = render_template('anonymous_usage.html', user=flask_login.current_user,
                           statistics=statistic_trackables, states=state_trackables)
    return html


@app.route('/usage/trackables', methods=['GET'])
@flask_login.login_required
def get_trackable_list():
    data = {'states': [q.name for q in db.session.query(State.name.distinct().label('name'))],
            'statistics': [q.name for q in db.session.query(Statistic.name.distinct().label('name'))]}

    return flask.jsonify(data)


@app.route('/usage/states', methods=['GET'])
@flask_login.login_required
def get_states():
    state_trackables = [q.name for q in db.session.query(State.name.distinct().label('name')) \
                                                  .filter(State.group_id == flask_login.current_user.group.id)\
                                                  .all()]
    return flask.jsonify({'states': state_trackables})


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
            # Get the UUID row or create one if it doesn't exist
            uuid = UUID.query.filter(UUID.user_identifier==payload['User Identifier']).first()
            if uuid is None:
                uuid = UUID(payload['User Identifier'])
                uuid.group.append(user.group)
                db.session.add(uuid)

            trackable = cls.query.filter(cls.name == trackable_name,
                                         cls.application_name == payload['Application Name'],
                                         cls.uuid_id == uuid.id,
                                         cls.group_id == user.group_id).first()
            if trackable is None:
                trackable = cls(trackable_name, uuid, payload['Application Name'], payload['Application Version'], user.group)
                db.session.add(trackable)
            # Apply the value of the data to the row
            if data['type'] == 'State':
                trackable.state = data['data']
            else:
                trackable.count = data['data']
        db.session.commit()
        return 'Success'

