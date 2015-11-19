__author__ = 'calvin'

import requests


def upload_report(payload):
    """
    Upload a report to the server.
    :param payload: Dictionary (JSON serializable) of crash data.
    :return: server response
    """
    js = json.dumps(payload)
    r = requests.post("http://127.0.0.1:5000/reports/upload", data=js)
    return r


def delete_report(report_number):
    """
    Delete a specific crash report from the server.
    :param report_number: Report Number
    :return: server response
    """
    js = json.dumps({'report_number': report_number})
    r = requests.post("http://127.0.0.1:5000/reports/delete", data=report_number)
    return r

if __name__ == '__main__':
    import json
    with open('./crash_report_test.json', 'rb') as f:
        js = json.load(f)

    # r1 = upload_report(js)
    r2 = delete_report('4')
    aqsd=3