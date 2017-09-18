import json
import flask
from flask import request
from sqlalchemy import func

from ...models import Statistic, State, Timer, Sequence, UUID, User, Application, Alias, Group
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

            application = Application.get_application(payload['Application Name'], payload['Application Version'])
            version_parsed = Application.parse_version_string(payload['Application Version'])

            if application is None:
                # Create the Application row if it doesn't already exist
                application = Application(payload['Application Name'], version_parsed, user.group)
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



@app.route('/usage/trackables', methods=['GET'])
def get_trackables():
    types = request.args.get('type', None)
    api_key = request.args.get('api_key', None)
    application_name = request.args.get('application', None)

    if api_key is None:
        flask.abort(flask.Response('You must provide a value for api_key', status=400))
    else:
        group_id, = db.session.query(User.group_id).filter(User.api_key == api_key).first()

    if types is None:
        types = TRACKABLES.keys()
    else:
        types = types.split(',')

    data = {t.capitalize(): {} for t in types}

    applications = db.session.query(Application.name, Application.id)\
                             .distinct()\
                             .filter(Application.group_id==group_id)
    if application_name:
        applications = applications.filter(Application.name == application_name)
    for t in types:
        t = t.capitalize()
        cls = TRACKABLES[t.capitalize()]

        for app, app_id in applications:
            q = db.session.query(cls.name.distinct()).join(Application).filter(Application.id==app_id,
                                                                               cls.group_id==group_id)
            if app not in data[t]:
                data[t][app] = set()
            data[t][app].update(set(s for s, in q.all()))

    for t in types:
        for app in data[t]:
            data[t][app] = list(data[t][app])

    return flask.jsonify(data)


@app.route('/usage/trackables/<trackable_type>', methods=['GET'])
def get_statistics(trackable_type):
    sortby = request.args.get('sortby', 'trackable')
    trackable = request.args.get('trackable', None)
    api_key = request.args.get('api_key', None)
    include_aliases = request.args.get('include_aliases', True)

    if api_key is None:
        flask.abort(flask.Response('You must provide a value for api_key', status=400))
    else:
        group_id = db.session.query(User.group_id).filter(User.api_key == api_key).first()
        if group_id is None:
            flask.abort(flask.Response('Invalid api_key', status=400))
        else:
            group_id = group_id[0]

    cls = {'statistics': Statistic, 'timers': Timer, 'sequences': Sequence}.get(trackable_type)
    if cls is None:
        flask.abort(400)

    data = {}

    if sortby == 'application':
        # return list of (trackable name, cummulative value, number of users) keyed by application name
        sort_query = db.session.query(Application.name)\
                                .distinct()\
                                .filter(Application.group_id==group_id)
        for app_name, in sort_query:

            q = db.session.query(cls.name, func.sum(cls.count), func.count(cls.id)) \
                          .join(cls.application) \
                          .filter(Application.name==app_name) \
                          .group_by(cls.name)

            if include_aliases == 'false':
                q = q.filter(cls.uuid.has(alias=None))
            if trackable:
                q = q.filter(cls.name==trackable)
            if q.count():
                data[app_name] = q.all()

    elif sortby == 'uuid':
        # return list of (trackable name, cummulative value) keyed by UUID
        sort_query = db.session.query(UUID.user_identifier)\
                               .distinct()\
                               .filter(UUID.group_id==group_id)

        for user_id, in sort_query:
            q = db.session.query(cls.name, cls.count) \
                          .join(cls.uuid) \
                          .filter(UUID.user_identifier==user_id,
                                  UUID.group_id == group_id) \

            if include_aliases == 'false':
                q = q.filter(cls.uuid.has(alias=None))
            if trackable:
                q = q.filter(cls.name==trackable)
            if q.count():
                data[user_id] = q.all()

    elif sortby == 'trackable':
        # return list of (application name, cummulative value, number of users) keyed by trackable name
        if trackable is not None:
            sort_query = [(trackable,)]
        else:
            sort_query = db.session.query(cls.name) \
                                   .distinct() \
                                   .filter(cls.group_id == group_id)

        for tr, in sort_query:
            q = db.session.query(Application.name, func.sum(cls.count), func.count(cls.id)) \
                                 .join(cls.application) \
                                 .filter(cls.name==tr,
                                         Application.group_id == group_id
                                         )\
                                 .group_by(Application.name)
            if include_aliases == 'false':
                q = q.filter(cls.uuid.has(alias=None))
            if q.count():
                data[tr] = q.all()
    else:
        flask.abort(flask.Response("sortby field must be either 'application', 'uuid' or 'trackable' (default)", status=400))

    return flask.jsonify(data)


@app.route('/usage/trackables/states', methods=['GET'])
def get_states():
    sortby = request.args.get('sortby', 'trackable')
    trackable = request.args.get('trackable', None)
    api_key = request.args.get('api_key', None)
    include_aliases = request.args.get('include_aliases', True)

    if include_aliases not in ('false', 'true', True):
        flask.abort(flask.Response('Invalid argument for include_aliases', status=400))

    if api_key is None:
        flask.abort(flask.Response('You must provide a value for api_key', status=400))
    else:
        group_id = db.session.query(User.group_id).filter(User.api_key == api_key).first()
        if group_id is None:
            flask.abort(flask.Response('Invalid api_key', status=400))
        else:
            group_id = group_id[0]

    data = {}
    if sortby == 'application':
        # return list of (trackable name, state value, number of users) keyed by application name
        sort_query = db.session.query(Application.name) \
                               .join(State.application)\
                               .distinct() \
                               .filter(Application.group_id == group_id)
        if include_aliases == 'false':
            sort_query = sort_query.filter(State.uuid.has(alias=None))

        for app_name, in sort_query:

            q = db.session.query(State.name, State.state, func.count(State.state)) \
                          .join(State.application) \
                          .filter(Application.name == app_name) \
                          .group_by(State.name, State.state)
            if trackable:
                q = q.filter(State.name == trackable)
            if q.count():
                data[app_name] = q.all()

    elif sortby == 'uuid':
        # return list of (trackable name, application name, state value) keyed by application name
        sort_query = db.session.query(UUID.user_identifier) \
                               .join(State.uuid)\
                               .distinct() \
                               .filter(UUID.group_id == group_id)

        if include_aliases == 'false':
            sort_query = sort_query.filter(State.uuid.has(alias=None))

        for user_id, in sort_query:

            q = db.session.query(State.name, Application.name, State.state) \
                          .join(State.uuid, State.application) \
                          .filter(UUID.user_identifier == user_id)

            if trackable:
                q = q.filter(State.name == trackable)
            if q.count():
                data[user_id] = q.all()

    elif sortby == 'state':
        # return list of (trackable name, application name, number of users) keyed by state value
        if trackable is None:
            flask.abort(flask.Response('Must specify "trackable" when sorting by state', status=400))

        sort_query = db.session.query(State.state) \
                               .distinct() \
                               .filter(UUID.group_id == group_id, State.name == trackable)
        if include_aliases == 'false':
            sort_query = sort_query.filter(State.uuid.has(alias=None))

        for state, in sort_query:

            q = db.session.query(State.name, Application.name, func.count(State.state)) \
                          .filter(State.state == state)\
                          .join(State.uuid, State.application)
            if q.count():
                data[state] = q.all()

    elif sortby == 'trackable':
        # return list of (state value, application name, number of users) keyed by trackable name
        if trackable is not None:
            sort_query = [(trackable,)]
        else:
            sort_query = db.session.query(State.name) \
                                   .distinct() \
                                   .filter(State.group_id == group_id)

        for tr, in sort_query:
            q = db.session.query(State.state, Application.name, func.count(State.state)) \
                .join(State.application) \
                .filter(State.name == tr) \
                .group_by(Application.name, State.state)
            if include_aliases == 'false':
                q = q.filter(State.uuid.has(alias=None))

            if q.count():
                data[tr] = q.all()
    else:
        flask.abort(flask.Response("sortby field must be either 'application', 'state', 'uuid' or 'trackable' (default)", status=400))

    return flask.jsonify(data)


@app.route('/usage/users', methods=['GET'])
def get_users():
    api_key = request.args.get('api_key', None)
    include_aliases = request.args.get('include_aliases', True)

    if include_aliases not in ('false', 'true', True):
        flask.abort(flask.Response('Invalid argument for include_aliases', status=400))

    if api_key is None:
        flask.abort(flask.Response('You must provide a value for api_key', status=400))
    else:
        group_id = db.session.query(User.group_id).filter(User.api_key == api_key).first()
        if group_id is None:
            flask.abort(flask.Response('Invalid api_key', status=400))
        else:
            group_id = group_id[0]

    sort_query = db.session.query(Application.name) \
        .join(State.application) \
        .distinct() \
        .filter(Application.group_id == group_id)

    data = {}
    for app_name, in sort_query:
        for cls in TRACKABLES.itervalues():
            q = db.session.query(func.count(cls.id).label('total'))\
                                       .join(Application)\
                                       .filter(Application.name==app_name)\
                                       .group_by(cls.name)\
                                       .order_by('total DESC')

            if include_aliases == 'false':
                q = q.filter(cls.uuid.has(alias=None))

            if q.count():
                data[app_name] = q.first()[0]

    return flask.jsonify(data)
