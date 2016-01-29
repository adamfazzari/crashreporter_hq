
import json

from flask import request, render_template, flash, redirect, url_for

from .. import app
from ..tools import save_report, delete_report as _delete_report


@app.route('/reports/delete/<int:report_number>', methods=['POST'])
def delete_report(report_number):
    success = _delete_report(report_number)
    if success:
        response = 'Success. Crash report #%d deleted' % report_number
    else:
        response = 'Failed. Crash report #%d does not exist.' % report_number
    flash(response)
    return redirect(url_for('home'))


@app.route('/reports/upload', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        payload = json.loads(request.data)
        cr, response = save_report(payload)
        return response
    else:
        return 'Upload failed'


@app.route('/reports/upload_many', methods=['POST'])
def upload_many():
    if request.method == 'POST':
        payload = json.loads(request.data)
        for package in payload:
            cr, response = save_report(package)
        return response
    else:
        return 'Upload failed'
