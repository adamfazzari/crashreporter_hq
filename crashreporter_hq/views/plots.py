import flask
from groups import *
from constants import *
from sqlalchemy.orm import aliased


@app.route('/plots/statistics', methods=['GET'])
@flask_login.login_required
def get_statistic_plots():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'

    plots = StatisticBarPlot.query.filter(StatisticBarPlot.group_id==flask_login.current_user.group.id).all()
    data = {p.id: {'name': p.name, 'application': p.application_name, 'statistics': p.statistics} for p in plots}
    return flask.jsonify(data)


@app.route('/plots/statistics/data', methods=['GET'])
@flask_login.login_required
def get_statistic_plot_data():
    if request.args.get('id'):
        plot = StatisticBarPlot.query.filter(StatisticBarPlot.id == int(request.args.get('id')),
                                             StatisticBarPlot.group_id == flask_login.current_user.group.id).first()

        stats = zip(*db.session.query(Statistic.name.distinct()).filter(Statistic.name.in_(plot.statistics)).all())[0]

        if request.args.get('alias_level', ANY) == NONE:
            uuids = UUID.query.outerjoin(Alias).filter(UUID.group_id == plot.group_id, Alias.id == None).all()
        elif request.args.get('alias_level', ANY) == ONLY:
            uuids = UUID.query.join(Alias).filter(UUID.group_id == plot.group_id).all()
        else:
            uuids = plot.group.uuids

        d = []
        for s in stats:
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


@app.route('/plots/states/data', methods=['GET'])
@flask_login.login_required
def get_state_plot_data():
    alias = aliased(State.uuid)
    if request.args.get('alias_level', False) == NONE:
        _aliases_id = set(u.uuid.id for u in flask_login.current_user.group.aliases)
        alias_filter = alias.id.notin_(_aliases_id)
    elif request.args.get('alias_level', False) == ONLY:
        _aliases_id = set(u.uuid.id for u in flask_login.current_user.group.aliases)
        alias_filter = alias.id.in_(_aliases_id)
    else:
        # ANY
        alias_filter = True # Do nothing
    data = {'name': request.args.get('name'),
            'counts': db.session.query(State.state, func.count(State.id)).join(alias)\
                                .filter(State.name==request.args.get('name'), alias_filter,
                                        State.group_id==flask_login.current_user.group.id)\
                                .group_by(State.state).all()
                    }

    return flask.jsonify(data)
