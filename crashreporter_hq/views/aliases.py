import flask
from groups import *
from ..models import Application


@app.route('/aliases', methods=['GET'])
@flask_login.login_required
def get_aliases():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    aliases = db.session.query(Alias).filter(Alias.group_id==group.id).all()
    aliases = {a.id: {'alias': a.alias, 'uuid': a.uuid.user_identifier} for a in aliases}
    data = flask.jsonify(aliases)
    return data


@app.route('/aliases/add', methods=['POST'])
@flask_login.login_required
def add_alias():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'

    uuid = UUID.query.filter(UUID.user_identifier == request.args['uuid']).first()
    if uuid:
        alias = Alias(flask_login.current_user.group, request.args['alias'], uuid)
        db.session.add(alias)
        db.session.commit()
        return 'Alias {a.alias} has been added for {a.uuid.user_identifier}'.format(a=alias)
    else:
        return 'Invalid UUID : {uuid}'.format(uuid=request.args['uuid'])


@app.route('/aliases/remove', methods=['POST'])
@flask_login.login_required
def remove_alias():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    alias_id = int(request.args.get('id', -1))
    if alias_id < 0:
        return flask.abort(404)

    alias = Alias.query.join(UUID).filter(Alias.group_id == flask_login.current_user.group_id,
                                          Alias.id == alias_id).first()

    if alias:
        db.session.delete(alias)
        db.session.commit()
        return 'Alias {a.alias} has been removed.'.format(a=alias)
    else:
        return flask.abort(404)

