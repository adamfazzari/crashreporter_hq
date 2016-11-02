import json

from flask import Response
from flask.ext.paginate import Pagination

from sqlalchemy import func, asc
from datetime import datetime

from groups import *
from ..models import CrashReport, UUID, Traceback, Application
from ..forms import YoutrackSubmitForm, SearchReportsForm

from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter


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
                           back_link=url_for('view_reports'))
    return html


@app.route('/reports/related/<int:report_id>')
def view_related_reports(report_id):
    PER_PAGE = 25
    report = CrashReport.query.filter(CrashReport.id == report_id).first()
    reports = CrashReport.query.filter(CrashReport.related_group_id == report.related_group_id).order_by('date').all()
    n_total_reports = len(reports)
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1
    reports = reports[(page-1) * PER_PAGE: page * PER_PAGE]
    pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
    aliases = {a.user_identifier: a.alias for a in flask_login.current_user.group.aliases}
    report_numbers = [str(r['Report Number']) for r in reports]

    html = render_template('related_reports.html', reports=reports,
                           user=flask_login.current_user,
                           pagination=pagination,
                           report_numbers=report_numbers,
                           aliases=aliases,
                           show_delete=True,
                           back_link=request.referrer)
    return html


@app.route('/reports/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_report_stats():
    top_reports = db.session.query(CrashReport, func.count(CrashReport.id).label('total'))\
                            .group_by(CrashReport. related_group_id)\
                            .order_by('total DESC')\
                            .limit(10).all()

    html = render_template('report_statistics.html', user=flask_login.current_user, top_reports=top_reports)
    return html


@app.route('/reports/get_stats', methods=['GET'])
def get_report_stats():
    if request.args.get('type') == 'date':
        # Query for the number of reports for each day
        q = db.session.query(func.date(CrashReport.date), func.count(func.DATE(CrashReport.date)))
        # Only dates that are before today (so we take out units with time-stamps in the future)
        q = q.filter(CrashReport.date <= datetime.now())
        # Group / bin the results by day in ascending order
        if request.args.get('hide_aliased', 'false') == 'true':
            q = q.filter(CrashReport.uuid_id.notin_([a.uuid_id for a in flask_login.current_user.group.aliases]))
        if request.args.get('released_only', 'false') == 'true':
            q = q.join(Application).filter(Application.is_release == True)
        q = q.group_by(func.date(CrashReport.date)).order_by(asc(CrashReport.date))

        # Because SQLite does not support the Date class in queries, we cannot cast the results
        # Instead, do the casting ourselves
        data = []
        for datestr, n in q.all():
            d = datetime.strptime(datestr, '%Y-%m-%d')
            data.append((d.year, d.month-1, d.day, d.hour, n))

    elif request.args.get('type') == 'user':
        # https://stackoverflow.com/questions/25500904/counting-relationships-in-sqlalchemy/25525771#25525771
        q = db.session.query(UUID.user_identifier, func.count(CrashReport.id)).join(UUID.reports).group_by(UUID.user_identifier)
        if request.args.get('hide_aliased', 'false') == 'true':
            q = q.filter(CrashReport.uuid_id.notin_([a.uuid_id for a in flask_login.current_user.group.aliases]))
        if request.args.get('released_only', 'false') == 'true':
            q = q.join(Application).filter(Application.is_release == True)
        data = q.all()
    else:
        return 'Invalid request'
    json_response = json.dumps(data)
    response = Response(json_response, content_type='application/json; charset=utf-8')
    response.headers.add('content-length', len(json_response))
    response.status_code = 200

    return response