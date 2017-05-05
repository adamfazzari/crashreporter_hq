import json
import flask_login
import flask
from flask import request
from sqlalchemy import func

from ...models import Statistic, State, Timer, Sequence, UUID, User, Application
from ... import app, db


TRACKABLES = {'Statistic': Statistic,
              'State': State,
              'Timer': Timer,
              'Sequence': Sequence}

TRACKABLE_ATTRS = {'Statistic': {'value': Statistic.count, 'sum': func.sum(Statistic.count)},
                    'State':    {'value': State.state,     'sum': func.count(State.state)},
                    'Timer':    {'value': Timer.time,      'sum': func.sum(Timer.count)},
                    'Sequence': {'value': Sequence.count,  'sum': func.sum(Sequence.count)}
                  }


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
                # Create the UUID row if it doesn't already exist
                uuid = UUID(payload['User Identifier'])
                uuid.group.append(user.group)
                db.session.add(uuid)

            # Parse the application version into a tuple
            app_version = payload['Application Version'].split('.')
            q = Application.query.filter(Application.name == payload['Application Name'])
            for ii, v in enumerate(app_version):
                q.filter(getattr(Application, 'version_%d' % ii) == int(v))
            application = q.first()

            if application is None:
                # Create the Application row if it doesn't already exist
                application = Application(payload['Application Name'], app_version)
                db.session.add(application)
                db.session.commit()

            trackable = cls.query.filter(cls.name == trackable_name,
                                         cls.application_id == application.id,
                                         cls.uuid_id == uuid.id,
                                         cls.group_id == user.group_id).first()
            if trackable is None:
                trackable = cls(trackable_name, uuid, application, user.group)
                db.session.add(trackable)
            # Apply the value of the data to the row
            if data['type'] == 'State':
                trackable.state = data['data']
            else:
                trackable.count = data['data']
        db.session.commit()
        return 'Success'


def _filter_trackables(q, trackable_class, **filters):
    if 'uuid' in filters:
        q = q.filter(UUID.user_identifier==filters['uuid'])
    if 'application' in filters:
        q = q.filter(trackable_class.application_name==filters['application'])
    if 'trackable' in filters:
        q = q.filter(trackable_class.name == filters['trackable'])

    return q

@app.route('/usage/trackables', methods=['GET'])
@flask_login.login_required
def get_trackables():
    types = request.args.get('type', None)

    data = {}
    if types is None:
        types = TRACKABLES.keys()
    else:
        types = types.split(',')

    for t in types:
        t = t.capitalize()
        cls = TRACKABLES[t.capitalize()]
        attr = TRACKABLE_ATTRS[t.capitalize()]['value']
        q = db.session.query(cls.name, Application.name, UUID.user_identifier, attr).join(UUID, Application)
        q = _filter_trackables(q, cls, **{k: v for k, v in request.args.iteritems()})
        q.filter(cls.group_id==flask_login.current_user.group_id)
        data[t] = q.all()

    return flask.jsonify(data)


@app.route('/usage/trackables/statistics', methods=['GET'])
@flask_login.login_required
def get_statistics():
    sortby = request.args.get('sortby', None)
    trackable = request.args.get('trackable', None)

    data = {}
    if sortby == 'application':
        for app_name, in db.session.query(Application.name)\
                                    .distinct()\
                                    .filter(Application.group_id==flask_login.current_user.group_id):

            q = db.session.query(Statistic.name, func.sum(Statistic.count)) \
                          .join(Statistic.application) \
                          .filter(Application.name==app_name) \
                          .group_by(Statistic.name)\

            if trackable:
                q = q.filter(Statistic.name==trackable)
            data[app_name] = q.all()

        return flask.jsonify(data)
    elif sortby == 'uuid':
        for user_id, in db.session.query(UUID.user_identifier)\
                                    .distinct()\
                                    .filter(UUID.group_id==flask_login.current_user.group_id):

            q = db.session.query(Statistic.name, func.sum(Statistic.count)) \
                          .join(Statistic.uuid) \
                          .filter(UUID.user_identifier==user_id) \

            if trackable:
                q = q.filter(Statistic.name==trackable)
            data[user_id] = q.all()

        return flask.jsonify(data)
    else:

        for tr, in ([(trackable,)] if trackable else []) or \
                    db.session.query(Statistic.name)\
                              .distinct()\
                              .filter(Statistic.group_id==flask_login.current_user.group_id):

            data[tr] = db.session.query(Application.name, func.sum(Statistic.count)) \
                               .join(Statistic.application) \
                               .filter(Statistic.name==tr) \
                               .group_by(Application.name)\
                               .all()
        return flask.jsonify(data)


@app.route('/usage/trackables/states', methods=['GET'])
@flask_login.login_required
def get_states():
    state_trackables = [q.name for q in db.session.query(State.name.distinct().label('name')) \
                                                  .filter(State.group_id == flask_login.current_user.group.id)\
                                                  .all()]
    return flask.jsonify({'states': state_trackables})

