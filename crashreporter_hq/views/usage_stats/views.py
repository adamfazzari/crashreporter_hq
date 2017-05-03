from ..groups import *
from ...models import Statistic, State, Timer, Sequence, UUID, StatisticBarPlot

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

@app.route('/usage', methods=['GET'])
def get_usage_data():
    pass
