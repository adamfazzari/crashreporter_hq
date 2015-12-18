
from flask.ext.paginate import Pagination


from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from ..config import *

from ..tools import get_similar_reports
from ..forms import YoutrackSubmitForm
from api import *
from login import *
from users import *
from ..extensions import views
from ..database import db_session
from ..models import CrashReport, Traceback


@app.route('/reports/<int:report_number>')
def view_report(report_number):
    cr = CrashReport.query.filter(CrashReport.id == report_number).first()
    tracebacks = Traceback.query.filter(Traceback.crashreport_id == report_number).all()
    pylexer = PythonLexer(stripall=True)
    highlighted_source = []
    for tb in tracebacks:
        highlighted_line = [tb['Error Line Number'] - tb['Module Line Number'] + 1]
        htmlformatter = HtmlFormatter(linenos=True,
                                      cssclass='highlight',
                                      linenostart=tb['Module Line Number'],
                                      hl_lines=highlighted_line)
        highlighted_source.append(highlight(tb['Source Code'], pylexer, htmlformatter))

    form = YoutrackSubmitForm()

    html = render_template('crashreport.html',
                           report=cr,
                           source_code=highlighted_source,
                           inspection_level=10000,
                           user=flask_login.current_user,
                           form=form,
                           back_link=url_for('home'))
    return html


@app.route('/reports/related/<int:related_group_id>')
def view_related_reports(related_group_id):
    PER_PAGE = 25
    reports = CrashReport.query.filter(CrashReport.related_group_id == related_group_id).order_by('date').all()
    n_total_reports = len(reports)
    try:
        page = max(1, int(request.args.get('page', n_total_reports / PER_PAGE)))
    except ValueError:
        page = 1
    reports = reports[(page-1) * PER_PAGE: page * PER_PAGE]
    pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
    html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination,
                           back_link=request.referrer)
    return html

@app.route('/')
@flask_login.login_required
def home():
    PER_PAGE = 25
    reports = get_similar_reports()
    n_total_reports = len(reports)
    try:
        page = max(1, int(request.args.get('page', n_total_reports / PER_PAGE)))
    except ValueError:
        page = 1
    reports = reports[(page-1) * PER_PAGE: page * PER_PAGE]
    pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
    html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination)
    return html
