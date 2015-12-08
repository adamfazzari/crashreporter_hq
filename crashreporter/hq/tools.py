
import json
import glob
import re

from collections import OrderedDict

from config import *


_report_cache = []
cr_number_regex = re.compile('crash_report_(\d+)\.json')


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


def get_reports():

    global _report_cache
    reports = []
    if len(os.listdir(UPLOAD_FOLDER)) - 1 != len(_report_cache):
        for r in glob.glob(os.path.join(UPLOAD_FOLDER, 'crash_report_*.json')):
            fullpath = os.path.join(UPLOAD_FOLDER, r)
            with open(fullpath) as _f:
                payload = json.load(_f)
            d = OrderedDict((('Report Number', cr_number_regex.findall(r)[0]),
                             ('Application Name', payload['Application Name']),
                             ('Application Version', payload['Application Version']),
                             ('User', payload['User']),
                             ('Error Type', payload['Error Type']),
                             ('Error Message', payload['Error Message']),
                             ('Date', payload['Date']),
                             ('Time', payload['Time'])
                             ))
            reports.append(d)
            reports.sort(key=lambda x: int(x['Report Number']))

        _report_cache = reports

    return _report_cache