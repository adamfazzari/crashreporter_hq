

from flask import request, render_template, flash, redirect, url_for
from sqlalchemy import func
import flask.ext.login as flask_login

from .. import app, db
from ..forms import CreateGroupForm, SearchForm, CreateAliasForm, PlotCreationForm
from ..models import Group, User, UUID, CrashReport, Alias, StatisticBarPlot, Statistic, State, Timer
from ..models.usagestats import TrackableTables


@app.route('/groups', methods=['GET', 'POST'], defaults={'group': None})
@app.route('/groups/<string:group>', methods=['GET', 'POST'])
@flask_login.login_required
def groups(group):
    sform = SearchForm(prefix='search')
    cform = CreateGroupForm(prefix='create')
    alias_form = CreateAliasForm()
    plot_form = PlotCreationForm()

    if request.method == 'GET':
        if group is None:
            g = flask_login.current_user.group
        else:
            g = Group.query.filter(Group.name == group).first()
            if g is None:
                flash('Group "{name}" does not exist.'.format(name=group))
                g = flask_login.current_user.group

        if flask_login.current_user.group_admin:
            uuids = g.uuids
        else:
            uuids = []

        trackables = {'statistics': db.session.query(Statistic, func.count(Statistic.id)).filter(Statistic.group_id==g.id).group_by(Statistic.name).all(),
                      'states': db.session.query(State, func.count(State.id)).filter(State.group_id==g.id).group_by(State.name).all(),
                      'timer': db.session.query(Timer, func.count(Timer.id)).filter(Timer.group_id==g.id).group_by(Timer.name).all(),
                      }
        return render_template('groups.html', sform=sform, cform=cform, alias_form=alias_form, plot_form=plot_form,
                                group=g, user=flask_login.current_user, uuids=uuids, trackables=trackables)

    elif cform.validate_on_submit() and cform.data['submit']:
        # Creating a group
        group = Group.query.filter(Group.name == cform.data['name']).first()
        if group is None:
            g = Group(cform.data['name'], description=cform.data['description'])
            user = flask_login.current_user
            user.group = g
            user.group_admin = True
            db.session.add(g)
            db.session.commit()
            flash('Group "{name}" has been created.'.format(**cform.data))
            return redirect(url_for('groups'))
        else:
            flash('Group "{name}" already exists.'.format(**cform.data))
            return redirect(url_for('groups'))
    elif sform.validate_on_submit() and sform.data['submit']:
        # Searching for a group
        return redirect(url_for('groups', group=sform.data['name']))


@app.route('/groups/request/join', methods=['POST'])
@flask_login.login_required
def group_join_request():
    group = request.args['group']
    loggedin_user = flask_login.current_user
    if loggedin_user.group.name == group and loggedin_user.group_admin:
        g = Group.query.filter(Group.name == group).first()
        q = User.query.filter(User.email == request.args['user_email'])
        u = q.first()
        if u in g.join_requests:
            g.join_requests.remove(u)
            g.join_requests_id = None
            db.session.commit()
            if request.args['action'] == 'accept':
                u.group = g
                db.session.commit()
            return redirect(url_for('groups', group=group))


@app.route('/groups/members', methods=['POST'])
@flask_login.login_required
def manage_member():
    group = request.args['group']
    loggedin_user = flask_login.current_user
    if loggedin_user.group.name == group and loggedin_user.group_admin:
        g = Group.query.filter(Group.name == group).first()
        u = User.query.filter(User.email == request.args['user_email'], User.group_id == g.id).first()
        if u:
            if request.args['action'] == 'remove':
                g.users.remove(u)
                u.group = None
                u.group_admin = False
            elif request.args['action'] == 'promote':
                u.group_admin = True
            elif request.args['action'] == 'demote':
                u.group_admin = False
            db.session.commit()
            return redirect(url_for('groups', group=group))


@app.route('/groups/request/request_invite', methods=['POST'])
@flask_login.login_required
def request_group_invite():
    # Current user has requested to join the group
    group = request.args['group']
    loggedin_user = flask_login.current_user
    if loggedin_user.group is None or (group != loggedin_user.group.name):
        g = Group.query.filter(Group.name == group).first()
        # Only request to join the group is the user isn't already in a group
        if flask_login.current_user not in g.join_requests:
            g.join_requests.append(flask_login.current_user)
            db.session.commit()
            flash('Request to join group "{name}" has been submitted.'.format(name=group))
        else:
            flash('Request to join group "{name}" has already been submitted.'.format(name=group))
        return redirect(url_for('groups', group=group))


@app.route('/uuids/<int:uuid_id>', methods=['POST'])
@flask_login.login_required
def manage_uuid(uuid_id):
    uuid = UUID.query.filter(UUID.id == uuid_id).first()
    if request.method == 'POST' and uuid:
        if request.args.get('action') == 'toggle_usage_stats':
            uuid.usagestats_black_listed = not uuid.usagestats_black_listed
            db.session.commit()
        elif request.args.get('action') == 'toggle_crash_reports':
            uuid.crashreport_black_listed = not uuid.crashreport_black_listed
            db.session.commit()
        elif request.args.get('action') == 'delete':
            for table in TrackableTables[:] + [CrashReport, Alias]:
                n_deleted = table.query.filter(table.uuid_id==uuid_id).delete()
                print n_deleted, table.__class__.__name__
            db.session.delete(uuid)
            db.session.commit()

    return redirect(request.referrer)


@app.route('/plots/manage', methods=['GET', 'POST'])
@flask_login.login_required
def manage_plots():
    if request.method == 'POST':
        if request.args.get('action') == 'create_bar_plot':

            plot_form = PlotCreationForm()
            if plot_form.validate_on_submit():
                fields = plot_form.data['fields'].split(',')
                stats = Statistic.query.filter(Statistic.name.in_(fields)).all()
                if stats:
                    plot = StatisticBarPlot(plot_form.data['name'],
                                            flask_login.current_user.group, *stats)
                    db.session.add(plot)
                    db.session.commit()
                    flash("New plot '%s' has been created" % plot.name)
                return redirect(request.referrer)

        elif request.args.get('action') == 'delete':

            if request.args.get('type') == 'statistic':
                if request.args.get('id'):
                    plot = StatisticBarPlot.query.filter(StatisticBarPlot.id == int(request.args.get('id'))).first()
                    if plot:
                        db.session.delete(plot)
                        db.session.commit()
                        flash("Plot '%s' has been deleted" % plot.name)
                return redirect(request.referrer)




