
from flask.ext.paginate import Pagination
from flask import Response

from sqlalchemy import func, asc
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from math import ceil
from ..config import *

from ..tools import get_similar_reports
from ..forms import YoutrackSubmitForm
from .. import db
from api import *
from login import *
from users import *
from groups import *
from ..forms import SearchReportsForm
from ..models import CrashReport, Traceback, Alias

import json

@app.route('/', methods=['GET'])
@flask_login.login_required
def home():
    PER_PAGE = 25
    q = get_similar_reports(return_query=True)
    if flask_login.current_user.group:
        form = SearchReportsForm()
        if request.args.get('field'):
            q = q.filter(CrashReport.group == flask_login.current_user.group,
                               getattr(CrashReport, request.args['field']).contains(str(request.args['value'])))
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
        aliases = {a.user_identifier: a.alias for a in flask_login.current_user.aliases}
        html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination,
                               aliases=aliases, form=form)
        return html
    else:
        return redirect(url_for('groups'))


@app.route('/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_stats():
    html = render_template('usage_stats.html', user=flask_login.current_user)
    return html

@app.route('/get_stats', methods=['GET'])
def get_stats():
    q = db.session.query(CrashReport.date, func.count(CrashReport.date)).group_by(CrashReport.user_identifier).\
                           order_by(asc(CrashReport.date))
    q2 = db.session.query(CrashReport.user_identifier, func.count(CrashReport.user_identifier).label('# crashes')).\
        group_by(CrashReport.user_identifier)
    data = {'date_data': [(d.year, d.month, d.day, d.hour, n) for d, n in q.all() if d.year == 2016],
            'user_data': q2.all()}

    json_response = json.dumps(data)
    response = Response(json_response, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(json_response))
    response.status_code = 200
    return response


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
    form = SearchReportsForm()
    html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination,
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