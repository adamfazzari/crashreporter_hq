__author__ = 'calvin'

import os
import time
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

@app.route('/reports/<int:report_number>')
def view_report(report_number):
    with open(os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % report_number)) as r:
        report = json.load(r)
        fields = {'date': 'TEMP',
                  'time': 'TEMP',
                  'traceback': report,
                  'error': 'SOME ERROR',
                  'app_name': 'TEST APP',
                  'app_version': 'ALPHA 1',
                  'user': 'CALVIN'
                  }
        html = render_template('crashreport.html', **fields)
        return html

@app.route('/')
def home():
    reports = []
    for r in os.listdir(UPLOAD_FOLDER):
        fullpath = os.path.join(UPLOAD_FOLDER, r)
        d = (OrderedDict((('Report Number', cr_number_regex.findall(r)[0]),
                         ('filename', r),
                         ('Date', time.ctime(os.path.getmtime(fullpath))),
                         ('Version', ''),
                         ('Error', ''))
                         ))
        reports.append(d)
    html = render_template('index.html', reports=reports)
    return html

@app.route('/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        tb_info = json.loads(request.data)
        num = len(os.listdir(UPLOAD_FOLDER)) + 1
        with open(os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % num), 'w') as cr:
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
