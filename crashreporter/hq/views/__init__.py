import glob
import re

from collections import OrderedDict

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from ..config import *

from api import *
from login import *
from users import *

cr_number_regex = re.compile('crash_report_(\d+)\.json')


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
@flask_login.login_required
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
    html = render_template('index.html', reports=reports, user=flask_login.current_user.get_id())
    return html
