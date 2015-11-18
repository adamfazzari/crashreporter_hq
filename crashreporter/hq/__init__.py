__author__ = 'calvin'

import os
import glob
import re
import json
from collections import OrderedDict
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename

cr_number_regex = re.compile('crash_report_(\d+)\.json')

HQ_FOLDER = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(HQ_FOLDER, 'templates')
UPLOAD_FOLDER = os.path.join(HQ_FOLDER, 'reports')
ALLOWED_EXTENSIONS = set(['html'])

app = Flask('hq', template_folder=TEMPLATE_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


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
        html = render_template('crashreport.html', info=payload)
        return html

@app.route('/')
def home():
    reports = []
    for r in glob.glob(os.path.join(UPLOAD_FOLDER, 'crash_report_*.json')):
        fullpath = os.path.join(UPLOAD_FOLDER, r)
        with open(fullpath) as _f:
            payload = json.load(_f)
        d = (OrderedDict((('Report Number', cr_number_regex.findall(r)[0]),
                         ('Application Name', payload['Application Name']),
                         ('Application Version', payload['Application Version']),
                         ('User', payload['User']),
                         ('Error Type', payload['Error Type']),
                         ('Error Message', payload['Error Message']),
                         ('Date', payload['Date']),
                         ('Time', payload['Time']),
                         ('Error', ''))
                         ))
        reports.append(d)
    html = render_template('index.html', reports=reports)
    return html

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        tb_info = json.loads(request.data)
        metadata = get_metadata()
        if metadata is not None:
            metadata['report_count'] += 1
        else:
            metadata = {'report_count': 1}

        with open(os.path.join(UPLOAD_FOLDER, '.metadata'), 'w') as metadata_file:
            json.dump(metadata, metadata_file)

        with open(os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % metadata['report_count']), 'w') as cr:
            json.dump(tb_info, cr,  sort_keys=True, indent=4)
            return 'Upload successful'
    return ''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def run_hq(debug):
    app.run(debug=debug)

if __name__ == '__main__':
    run_hq(True)
