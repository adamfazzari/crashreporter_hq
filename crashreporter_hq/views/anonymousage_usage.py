from flask import Response
from sqlalchemy import func

from groups import *
from ..models import Statistic, State, Timer, Sequence, UUID, StatisticBarPlot

import json

TRACKABLES = {'Statistic': Statistic, 'State': State, 'Timer': Timer, 'Sequence': Sequence}


@app.route('/usage/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_usage_stats():
    state_trackables = [q.name for q in db.session.query(State.name.distinct().label('name'))]
    plot_ids = [t[0] for t in db.session.query(StatisticBarPlot.id).filter(StatisticBarPlot.group_id==flask_login.current_user.group.id).all()]
    html = render_template('anonymous_usage.html', user=flask_login.current_user, plot_ids=plot_ids, states=state_trackables)
    return html


@app.route('/usage/get_state_list', methods=['GET'])
def get_state_list():
    data = [q.name for q in db.session.query(State.name.distinct().label('name'))]
    json_response = json.dumps(data)
    response = Response(json_response, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(json_response))
    response.status_code = 200
    return response


@app.route('/usage/get_data/plot', methods=['GET'])
def get_plot_data():
    if request.args.get('type') == 'statistic':
        if request.args.get('id'):
            plot = StatisticBarPlot.query.filter(StatisticBarPlot.id==int(request.args.get('id'))).first()
            q = db.session.query(Statistic.name, func.sum(Statistic.count))
            q = q.group_by(Statistic.name)
            q = q.filter(Statistic.id.in_([s.id for s in plot.statistics]))
            data = {'stats': q.all(),
                    'n_users': len(set(s.uuid for s in plot.statistics))}
    elif request.args.get('type') == 'state':
            data = {'name': request.args.get('name'),
                    'counts': db.session.query(State.state, func.count(State.id)).
                                       filter(State.name==request.args.get('name')).
                                       group_by(State.state).all()
                    }    #
    # else:
    #     return 'Invalid query.'
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
            # Get the UUID row or create one if it doesn't exist
            uuid = UUID.query.filter(UUID.user_identifier==payload['User Identifier']).first()
            if uuid is None:
                uuid = UUID(payload['User Identifier'])

            trackable = cls.query.filter(cls.name==trackable_name, cls.uuid_id==uuid.id, cls.group_id==user.group_id).first()
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

