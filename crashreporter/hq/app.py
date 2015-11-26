__author__ = 'clobo'

import os
import re
import glob
import json
from collections import OrderedDict

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from flask import Flask, request, render_template
from . import UPLOAD_FOLDER, STATIC_FOLDER, TEMPLATE_FOLDER

cr_number_regex = re.compile('crash_report_(\d+)\.json')

app = Flask('hq', static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def _delete_report(number):
    path = os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % number)
    if os.path.isfile(path):
        os.remove(path)
        return True
    else:
        return False


def _save_report(payload):
        metadata = get_metadata()
        if metadata is not None:
            metadata['report_count'] += 1
        else:
            metadata = {'report_count': 1}

        with open(os.path.join(UPLOAD_FOLDER, '.metadata'), 'w') as metadata_file:
            json.dump(metadata, metadata_file)

        with open(os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % metadata['report_count']), 'w') as cr:
            json.dump(payload, cr,  sort_keys=True, indent=4)


@app.route('/reports/delete/<int:report_number>', methods=['POST'])
def delete_report(report_number):
    success = _delete_report(report_number)
    if success:
        response = 'Success. Crash report #%d deleted' % report_number
    else:
        response = 'Failed. Crash report #%d does not exist.' % report_number
    return response


def get_metadata():
    metadata_fp = os.path.join(UPLOAD_FOLDER, '.metadata')
    if os.path.isfile(metadata_fp):
        with open(metadata_fp, 'r') as metadata_file:
            metadata = json.load(metadata_file)
            return metadata


@app.route('/reports/<int:report_number>')
def view_report(report_number):
    with open(os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % report_number)) as r:
        payload = json.load(r)
        pylexer = PythonLexer(stripall=True)
        for tb in payload['Traceback']:
            htmlformatter = HtmlFormatter(linenos=True, style='friendly', cssclass='highlight', linenostart=tb['Source Code'][0][0])
            src = highlight(''.join(t[1] for t in tb['Source Code']), pylexer, htmlformatter)
            tb['Source Code'] = src
        html = render_template('crashreport.html', info=payload, inspection_level=10000)
        return html


@app.route('/')
def home():
    reports = []
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
    html = render_template('index.html', reports=reports)
    return html


@app.route('/reports/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        payload = json.loads(request.data)
        _save_report(payload)
        return 'Upload successful'
    else:
        return 'Upload failed'


@app.route('/reports/upload_many', methods=['POST'])
def upload_many():
    if request.method == 'POST':
        payload = json.loads(request.data)
        for package in payload:
            _save_report(package)
        return 'Upload successful'
    else:
        return 'Upload failed'


def run_hq(debug):
    app.run(debug=debug)


if __name__ == '__main__':
    run_hq(True)
