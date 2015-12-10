
from flask.ext.paginate import Pagination


from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from ..config import *

from ..tools import get_reports

from api import *
from login import *
from users import *


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
        html = render_template('crashreport.html',
                               info=payload,
                               inspection_level=10000,
                               user=flask_login.current_user)
        return html


@app.route('/')
@flask_login.login_required
def home():
    PER_PAGE = 50
    reports = get_reports()
    n_total_reports = len(reports)
    try:
        page = max(1, int(request.args.get('page', n_total_reports / PER_PAGE)))
    except ValueError:
        page = 1
    reports = reports[(page-1) * PER_PAGE: page * PER_PAGE]
    pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
    html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination)
    return html
