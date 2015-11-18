__author__ = 'calvin'

import os
import time
import re
from collections import OrderedDict
from flask import Flask, request, redirect, url_for, send_from_directory, render_template
from werkzeug import secure_filename

cr_number_regex = re.compile('crashreport(\d+)\..*')

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
    with open(os.path.join(UPLOAD_FOLDER, 'crashreport%d.html' % report_number)) as r:
        html = r.read()
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
        fileobject = request.files['files']
        if fileobject and allowed_file(fileobject.filename):
            filename = secure_filename(fileobject.filename)

            fileobject.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for('uploaded_file', filename=filename))
    return ''

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'],
                               filename)

def run_hq(debug):
    app.run(debug=debug)

if __name__ == '__main__':
    run_hq(True)
