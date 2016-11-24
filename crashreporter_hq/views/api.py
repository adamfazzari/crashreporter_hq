
import json

from flask import request

from .. import app
from ..tools import save_report



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
