
import json

from config import *


def get_metadata():
    metadata_fp = os.path.join(UPLOAD_FOLDER, '.metadata')
    if os.path.isfile(metadata_fp):
        with open(metadata_fp, 'r') as metadata_file:
            metadata = json.load(metadata_file)
            return metadata


def delete_report(number):
    path = os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % number)
    if os.path.isfile(path):
        os.remove(path)
        return True
    else:
        return False


def save_report(payload):
        metadata = get_metadata()
        if metadata is not None:
            metadata['report_count'] += 1
        else:
            metadata = {'report_count': 1}

        with open(os.path.join(UPLOAD_FOLDER, '.metadata'), 'w') as metadata_file:
            json.dump(metadata, metadata_file)

        with open(os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % metadata['report_count']), 'w') as cr:
            json.dump(payload, cr,  sort_keys=True, indent=4)

