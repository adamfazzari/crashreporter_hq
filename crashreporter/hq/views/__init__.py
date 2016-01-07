
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
from ..forms import CreateGroupForm
from ..models import CrashReport, Traceback, Group


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

@app.route('/groups', methods=['GET', 'POST'])
@flask_login.login_required
def groups():
    form = CreateGroupForm()
    if request.method == 'GET':
        return render_template('groups.html', form=form)
    elif form.validate_on_submit():
        group = Group.query.filter(Group.name == form.data['name']).first()
        if group is None:
            g = Group(form.data['name'])
            user = flask_login.current_user
            user.group = g
            user.group_admin = True
            db_session.add(g)
            db_session.commit()
            flash('Group "{name}" has been created.'.format(**form.data))
            return redirect(url_for('group_page', name=g.name))


@app.route('/groups/<string:name>')
@flask_login.login_required
def group_page(name):
    if request.method == 'GET':
        group = Group.query.filter(Group.name == name).first()
        if group is None:
            return 'Invalid group name.'
        else:
            return render_template('group_page.html', group=group)


@app.route('/')
@flask_login.login_required
def home():
    PER_PAGE = 25
    q = get_similar_reports(return_query=True)
    if flask_login.current_user.group:
        reports = q.filter(CrashReport.group == flask_login.current_user.group).all()
        n_total_reports = len(reports)
        try:
            page = max(1, int(request.args.get('page', n_total_reports / PER_PAGE)))
        except ValueError:
            page = 1
        reports = reports[(page-1) * PER_PAGE: page * PER_PAGE]
        pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
        html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination)
        return html
    else:
        return redirect(url_for('groups'))

