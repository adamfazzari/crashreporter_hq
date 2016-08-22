
from flask.ext.paginate import Pagination
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from math import ceil
from sqlalchemy import or_
from datetime import datetime

from ..tools import get_similar_reports
from ..forms import YoutrackSubmitForm
from api import *
from login import *
from users import *
from groups import *
from anonymousage_usage import *
from report_stats import *
from ..config import *
from ..forms import SearchReportsForm
from ..models import CrashReport, Traceback


@app.route('/', methods=['GET'])
@flask_login.login_required
def home():
    PER_PAGE = 25
    q = get_similar_reports(return_query=True)
    if flask_login.current_user.group:
        form = SearchReportsForm()
        if request.args.get('field'):
            value = request.args['value']
            if request.args['field'] == 'user_identifier':
                # Search the user identifiers associated with any aliases that may be part of the search
                attr = getattr(CrashReport, request.args['field'])
                logic_or = or_(attr.contains(a.user_identifier) for a in flask_login.current_user.group.aliases if value in a.alias)
                q = q.filter(CrashReport.group == flask_login.current_user.group, logic_or)
            elif request.args['field'] == 'before_date':
                date = datetime.strptime(value, '%d %B %Y')
                q = q.filter(CrashReport.group == flask_login.current_user.group,
                        CrashReport.date <= date)
            elif request.args['field'] == 'after_date':
                date = datetime.strptime(value, '%d %B %Y')
                q = q.filter(CrashReport.group == flask_login.current_user.group,
                             CrashReport.date >= date)

            else:
                attr = getattr(CrashReport, request.args['field'])
                q = q.filter(CrashReport.group == flask_login.current_user.group, attr.contains(str(value)))
        else:
            q = q.filter(CrashReport.group == flask_login.current_user.group)

        reports = q.order_by(CrashReport.id.asc()).all()

        n_total_reports = len(reports)
        max_page = int(ceil(n_total_reports / float(PER_PAGE)))
        try:
            page = max(1, int(request.args.get('page', 1)))
        except ValueError:
            page = 1
        page_rev = max_page - page + 1
        reports = reports[(page_rev-1) * PER_PAGE: page_rev * PER_PAGE]
        pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
        aliases = {a.user_identifier: a.alias for a in flask_login.current_user.group.aliases}
        html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination,
                               aliases=aliases, form=form)
        return html
    else:
        return redirect(url_for('groups'))


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


@app.route('/reports/related/<int:report_id>')
def view_related_reports(report_id):
    PER_PAGE = 25
    report = CrashReport.query.filter(CrashReport.id == report_id).first()
    reports = CrashReport.query.filter(CrashReport.related_group_id == report.related_group_id).order_by('date').all()
    n_total_reports = len(reports)
    try:
        page = max(1, int(request.args.get('page', n_total_reports / PER_PAGE)))
    except ValueError:
        page = 1
    reports = reports[(page-1) * PER_PAGE: page * PER_PAGE]
    pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
    form = SearchReportsForm()
    aliases = {a.user_identifier: a.alias for a in flask_login.current_user.group.aliases}
    html = render_template('index.html', reports=reports,
                           user=flask_login.current_user,
                           pagination=pagination,
                           aliases=aliases,
                           back_link=request.referrer)
    return html

@app.route('/search', methods=['GET', 'POST'])
@flask_login.login_required
def search():
    form = SearchReportsForm()
    if flask_login.current_user.group and form.validate_on_submit():
        return redirect(url_for('home', **form.data))
    else:
        return redirect(url_for('home'))