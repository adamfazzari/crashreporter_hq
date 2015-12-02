
import json

from flask import request, render_template, flash, redirect, url_for

from .. import app
from ..tools import save_report


@app.route('/reports/delete/<int:report_number>', methods=['POST'])
def delete_report(report_number):
    success = delete_report(report_number)
    if success:
        response = 'Success. Crash report #%d deleted' % report_number
    else:
        response = 'Failed. Crash report #%d does not exist.' % report_number
    return response


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
