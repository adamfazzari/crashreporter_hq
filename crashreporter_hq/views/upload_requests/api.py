import flask
from flask import request

from ...models import UploadRequest, User
from ... import app, db


@app.route('/upload_requests', methods=['GET'])
def get_upload_requests():
    api_key = request.args.get('api_key', None)

    if api_key is None:
        flask.abort(flask.Response('You must provide a value for api_key', status=400))
    else:
        group_id, = db.session.query(User.group_id).filter(User.api_key == api_key).first()

    sort_query = db.session.query(UploadRequest.geohash,
                                  UploadRequest.crash_reports,
                                  UploadRequest.usage_stats) \
        .distinct()

    data = {}
    for gh, cr, us in sort_query:
        data[gh] = {'crash_reports': cr,
                    'usage_stats': us}

    return flask.jsonify(data)

