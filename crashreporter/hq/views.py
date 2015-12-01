
import glob
import json
import re

from collections import OrderedDict

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from flask import request, render_template

from tools import delete_report

from . import app
from config import *
from tools import save_report

cr_number_regex = re.compile('crash_report_(\d+)\.json')


@app.route('/reports/delete/<int:report_number>', methods=['POST'])
def delete_report(report_number):
    success = delete_report(report_number)
    if success:
        response = 'Success. Crash report #%d deleted' % report_number
    else:
        response = 'Failed. Crash report #%d does not exist.' % report_number
    return response


@app.route('/reports/<int:report_number>')
def view_report(report_number):
    with open(os.path.join(UPLOAD_FOLDER, 'crash_report_%d.json' % report_number)) as r:
        payload = json.load(r)
        pylexer = PythonLexer(stripall=True)
        for tb in payload['Traceback']:
            highlighted_line = [tb['Error Line Number'] - tb['Source Code'][0][0] + 1]
            htmlformatter = HtmlFormatter(linenos=True,
                                          cssclass='highlight',
                                          linenostart=tb['Source Code'][0][0],
                                          hl_lines=highlighted_line)
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
        save_report(payload)
        return 'Upload successful'
    else:
        return 'Upload failed'


@app.route('/reports/upload_many', methods=['POST'])
def upload_many():
    if request.method == 'POST':
        payload = json.loads(request.data)
        for package in payload:
            save_report(package)
        return 'Upload successful'
    else:
        return 'Upload failed'
