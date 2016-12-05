import json
from datetime import datetime

from flask import Response
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from sqlalchemy import asc

from groups import *

from ..models import CrashReport, UUID, Traceback, Application
from ..tools import save_report, delete_report as _delete_report
from ..extensions import search


@app.route('/reports/<int:report_number>')
@flask_login.login_required
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

    alias = Alias.query.filter(Alias.uuid_id==cr.uuid_id).first()
    html = render_template('crashreport.html',
                           report=cr,
                           source_code=highlighted_source,
                           inspection_level=10000,
                           alias=alias,
                           search_links={'Google': search.get_search_link('google', cr.error_message),
                                         'StackOverflow': search.get_search_link('stackoverflow', cr.error_message)},
                           back_link=url_for('view_reports'))
    return html


@app.route('/reports/related/<int:report_id>')
@flask_login.login_required
def view_related_reports(report_id):
    return render_template('index.html', user=flask_login.current_user,
                    search_init="{related_to_id: %d}" % report_id)


@app.route('/reports/<int:report_number>/info', methods=['GET'])
@flask_login.login_required
def get_report_info(report_number):
    user = flask_login.current_user
    group = user.group
    aliases = {a.user_identifier: a.alias for a in group.aliases}
    report = CrashReport.query.filter(CrashReport.id == report_number).first()
    if report:
        return flask.jsonify(report_to_json(report, aliases=aliases))


def report_to_json(report, aliases=None):
    if aliases is None:
        user = report.uuid.user_identifier
    else:
        user = aliases.get(report.uuid.user_identifier, report.uuid.user_identifier)
    return {'report_number': report.id,
             'related_report_numbers': [r.id for r in report.related_reports],
             'application_name': report.application.name,
             'application_version': report.application.version_string,
             'is_release': report.application.is_release,
             'user': user,
             'error_type': report.error_type,
             'error_message': report.error_message,
             'date': report.date.strftime('%B %d %Y'),
             'time': report.date.strftime('%I:%M %p')
             }

@app.route('/reports/delete', methods=['POST'])
@flask_login.login_required
def delete_many_reports():
    report_numbers = map(int, request.args.get('report_numbers').split(','))
    delete_similar = request.args.get('delete_similar') == 'True'
    success = _delete_report(delete_similar, *report_numbers)
    if success:
        response = 'Success. Crash report #%s deleted' % request.args.get('report_numbers')
    else:
        response = 'Failed. Crash report #%s does not exist.' % request.args.get('report_numbers')
    flash(response)
    return redirect(url_for('view_reports'))


@app.route('/reports/<int:report_id>/delete', methods=['POST'])
@flask_login.login_required
def delete_single_report(report_id):
    delete_similar = False
    success = _delete_report(delete_similar, report_id)
    if success:
        return 'Success. Crash report #%d deleted' % report_id
    else:
        return 'Failed. Crash report #%d does not exist.' % report_id


@app.route('/reports/upload', methods=['POST'])
def upload_single_report():
    if request.method == 'POST':
        payload = json.loads(request.data)
        cr, response = save_report(payload)
        return response
    else:
        return 'Upload failed'


@app.route('/reports/upload_many', methods=['POST'])
def upload_many_reports():
    if request.method == 'POST':
        payload = json.loads(request.data)
        for package in payload:
            cr, response = save_report(package)
        return response
    else:
        return 'Upload failed'


@app.route('/reports/view_stats', methods=['GET', 'POST'])
@flask_login.login_required
def view_report_stats():
    group = flask_login.current_user.group
    if group is None:
        return 'You are not in a group.'
    latest_applications = db.session.query(func.max(Application.version_0),
                                           func.max(Application.version_1),
                                           func.max(Application.version_2)) \
                                    .filter(Application.group_id==group.id,
                                            Application.is_release == True) \
                                    .group_by(Application.name).all()

    top_reports = {}
    for v0, v1, v2 in latest_applications:
        r = db.session.query(CrashReport, func.count(CrashReport.id).label('total'))\
                      .group_by(CrashReport.related_group_id) \
                      .filter(CrashReport.group_id==group.id,
                              CrashReport.application.has(version_0=v0, version_1=v1, version_2=v2)) \
                      .order_by('total DESC').limit(5)
        if r:
            top_reports[r[0][0].application.name] = r

    html = render_template('report_statistics.html', user=flask_login.current_user, top_reports=top_reports)
    return html


@app.route('/reports/get_stats', methods=['GET'])
@flask_login.login_required
def get_report_stats():
    group = flask_login.current_user.group
    if request.args.get('type') == 'date':
        # Query for the number of reports for each day
        q = db.session.query(func.date(CrashReport.date), func.count(func.DATE(CrashReport.date)))\
                      .filter(CrashReport.group_id==group.id)
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
        q = db.session.query(UUID.user_identifier, func.count(CrashReport.id))\
                      .filter(CrashReport.group_id==group.id)\
                      .join(UUID.reports)\
                      .group_by(UUID.user_identifier)
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