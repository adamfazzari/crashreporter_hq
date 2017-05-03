import json
from flask import request

from ...models import Statistic, State, Timer, Sequence, UUID, User
from ... import app, db


TRACKABLES = {'Statistic': Statistic,
              'State': State,
              'Timer': Timer,
              'Sequence': Sequence}


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
                uuid = UUID(payload['User Identifier'])
                uuid.group.append(user.group)
                db.session.add(uuid)

            trackable = cls.query.filter(cls.name == trackable_name,
                                         cls.application_name == payload['Application Name'],
                                         cls.uuid_id == uuid.id,
                                         cls.group_id == user.group_id).first()
            if trackable is None:
                trackable = cls(trackable_name, uuid, payload['Application Name'], payload['Application Version'], user.group)
                db.session.add(trackable)
            # Apply the value of the data to the row
            if data['type'] == 'State':
                trackable.state = data['data']
            else:
                trackable.count = data['data']
        db.session.commit()
        return 'Success'

# @app.route('/usage', methods=['GET'])
# def get_usage_data():
#     pass
