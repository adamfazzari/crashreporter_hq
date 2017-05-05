from ..groups import *
from ...models import Statistic, State, Timer, Sequence, UUID, StatisticBarPlot

TRACKABLES = {'Statistic': Statistic, 'State': State, 'Timer': Timer, 'Sequence': Sequence}


@app.route('/usage/plots', methods=['GET', 'POST'])
@flask_login.login_required
def usage_plots():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    state_trackables = [q.name for q in db.session.query(State.name.distinct().label('name'))]
    statistic_trackables = [t for t in db.session.query(StatisticBarPlot.id, StatisticBarPlot.name)\
                                                 .filter(StatisticBarPlot.group_id==group.id).all()]
    html = render_template('anonymous_usage.html', user=flask_login.current_user,
                           statistics=statistic_trackables, states=state_trackables)
    return html

