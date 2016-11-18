import flask
from groups import *
from constants import *


@app.route('/plots/statistics', methods=['GET'])
@flask_login.login_required
def get_statistic_plots():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'

    plots = StatisticBarPlot.query.all()
    data = {p.id: {'name': p.name, 'application': p.application_name, 'statistics': p.statistics} for p in plots}
    return flask.jsonify(data)


@app.route('/plots/statistics/data', methods=['GET'])
@flask_login.login_required
def get_statistic_plot_data():
    if request.args.get('id'):
        plot = StatisticBarPlot.query.filter(StatisticBarPlot.id == int(request.args.get('id')),
                                             StatisticBarPlot.group_id == flask_login.current_user.group.id).first()
        if int(request.args.get('hide_aliases', ANY)) == NONE:
            _aliases = set(u.uuid for u in plot.group.aliases)
            uuids = filter(lambda x: x not in _aliases, plot.group.uuids)
        elif int(request.args.get('hide_aliases', ANY)) == ONLY:
            _aliases = set(u.uuid for u in plot.group.aliases)
            uuids = filter(lambda x: x in _aliases, plot.group.uuids)
        else:
            uuids = plot.group.uuids
        d = []
        stats = db.session.query(Statistic.name.distinct()).filter(Statistic.name.in_(plot.statistics)).all()
        for s in zip(*stats)[0]:
            d2 = [s]
            for u in uuids:
                count = db.session.query(Statistic.count).filter(Statistic.uuid_id == u.id, Statistic.name == s).first()
                d2.append(count[0] if count else 0)
            d.append(d2)
        aliases = {a.uuid.id: a.alias for a in plot.group.aliases}
        data = {'uuids': [aliases.get(u.id, u.user_identifier) for u in uuids],
                'counts': d,
                'n_users': len(uuids)}
        return flask.jsonify(data)


@app.route('/plots/statistics/add', methods=['POST'])
@flask_login.login_required
def add_statistic_plot():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    data = request.get_json()
    fields = data['statistics']
    name = data['name']
    app = data.get('application', '')
    version = data.get('version', '')
    q = db.session.query(Statistic.name).filter(Statistic.name.in_(fields))
    if app:
        q.filter(Statistic.application_name==app)
    if version:
        q.filter(Statistic.application_version==version)
    stats = q.group_by(Statistic.name).all()
    if stats:
        plot = StatisticBarPlot(name,
                                flask_login.current_user.group, zip(*stats)[0])
        db.session.add(plot)
        db.session.commit()
        flash("New plot '%s' has been created" % plot.name)
        return redirect(request.referrer)


@app.route('/plots/statistics/remove', methods=['POST'])
@flask_login.login_required
def remove_statistic_plot():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    plot_id = int(request.args.get('id', -1))
    if plot_id > 0:
        plot = StatisticBarPlot.query.filter(StatisticBarPlot.id == plot_id).first()
        if plot:
            db.session.delete(plot)
            db.session.commit()
            flash("Plot '%s' has been deleted" % plot.name)
    return redirect(request.referrer)

