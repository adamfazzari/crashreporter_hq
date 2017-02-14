import flask
from groups import *
from ..models import Application


@app.route('/applications/releases', methods=['GET'])
@flask_login.login_required
def released_applications():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    latest_applications = db.session.query(Application) \
                                    .filter(Application.group_id==group.id,
                                            Application.is_release == True).all()
    latest_applications = {d.id : {'name': d.name, 'version': d.version_string} for d in latest_applications}
    data = flask.jsonify(latest_applications)
    return data


@app.route('/applications/releases/latest', methods=['GET'])
@flask_login.login_required
def latest_released_applications():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    latest_applications = db.session.query(Application.id,
                                           Application.name,
                                           func.max(Application.version_0),
                                           func.max(Application.version_1),
                                           func.max(Application.version_2)) \
                                    .filter(Application.group_id==group.id,
                                            Application.is_release == True) \
                                    .group_by(Application.name).all()

    data = flask.jsonify(latest_applications)
    return data

@app.route('/applications/releases/add', methods=['POST'])
@flask_login.login_required
def add_application_release():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'

    v0, v1, v2 = map(int, request.args['version'].split('.'))
    application = Application.query.filter(Application.name == request.args['name'],
                                           Application.version_0 == v0,
                                           Application.version_1 == v1,
                                           Application.version_2 == v2, ).first()
    if application:
        application.is_release = True
    else:
        application = Application(name=request.args['name'], version=(v0, v1, v2), is_release=True)
        db.session.add(application)
        group.add_application(application)
    db.session.commit()
    return 'Application {a.name} version {a.version_string} has been added'.format(a=application)


@app.route('/applications/releases/remove', methods=['POST'])
@flask_login.login_required
def remove_application_release():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'

    app_id = int(request.args.get('id', -1))
    if app_id < 0 :
        return flask.abort(404)
    application = Application.query.filter(Application.id == app_id).first()
    if application:
        application.is_release = False
        db.session.commit()
        return 'Application {a.name} version {a.version_string} has been removed'.format(a=application)
    else:
        return 'Failed to remove Application: {a.name} version {a.version_string}'.format(a=application)

