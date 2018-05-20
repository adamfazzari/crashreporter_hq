import json
import os
import flask
from flask import request

from ...models import Statistic, State, Timer, Sequence, UUID, User, Application, Alias, Group
from ... import app, db


@app.route('/admin/system_info', methods=['GET'])
def get_system_info():
    api_key = request.args.get('api_key', None)

    if api_key is None:
        flask.abort(flask.Response('You must provide a value for api_key', status=400))
    else:
        group_id, = db.session.query(User.group_id).filter(User.api_key == api_key).first()

    db_path = app.config['DB_ABSOLUTE_PATH']
    data = {}
    try:
        stats = os.stat(db_path)
        data['db_size_bytes'] = stats.st_size
    except os.error as e:
        flask.abort(flask.Response('Error retrieving database size', status=500))

    return flask.jsonify(data)

