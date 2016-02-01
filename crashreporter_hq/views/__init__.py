
from flask.ext.paginate import Pagination


from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter

from math import ceil
from ..config import *

from ..tools import get_similar_reports
from ..forms import YoutrackSubmitForm
from api import *
from login import *
from users import *
from ..extensions import views
from ..database import db_session
from ..forms import CreateGroupForm, SearchForm, SearchReportsForm
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


@app.route('/groups', methods=['GET', 'POST'], defaults={'group': None})
@app.route('/groups/<string:group>', methods=['GET', 'POST'])
@flask_login.login_required
def groups(group):
    sform = SearchForm(prefix='search')
    cform = CreateGroupForm(prefix='create')
    if request.method == 'GET':
        if group is None:
            g = flask_login.current_user.group
        else:
            g = Group.query.filter(Group.name == group).first()
            if g is None:
                flash('Group "{name}" does not exist.'.format(name=group))
                g = flask_login.current_user.group
        return render_template('groups.html', sform=sform, cform=cform, group=g, user=flask_login.current_user)
    elif cform.validate_on_submit() and cform.data['submit']:
        # Creating a group
        group = Group.query.filter(Group.name == cform.data['name']).first()
        if group is None:
            g = Group(cform.data['name'], description=cform.data['description'])
            user = flask_login.current_user
            user.group = g
            user.group_admin = True
            db_session.add(g)
            db_session.commit()
            flash('Group "{name}" has been created.'.format(**cform.data))
            return redirect(url_for('groups'))
        else:
            flash('Group "{name}" already exists.'.format(**cform.data))
            return redirect(url_for('groups'))
    elif sform.validate_on_submit() and sform.data['submit']:
        # Searching for a group
        return redirect(url_for('groups', group=sform.data['name']))


@app.route('/groups/request/accept_invite', methods=['POST'])
def accept_group_invite():
    group = request.args['group']
    loggedin_user = flask_login.current_user
    if loggedin_user.group.name == group and loggedin_user.group_admin:
        g = Group.query.filter(Group.name == group).first()
        q = User.query.filter(User.email == request.args['user_email'])
        u = q.first()
        if u in g.join_requests:
            g.join_requests.remove(u)
            g.users.append(u)
            db_session.commit()
            return redirect(url_for('groups', group=group))


@app.route('/groups/request/request_invite', methods=['POST'])
def request_group_invite():
    # Current user has requested to join the group
    group = request.args['group']
    loggedin_user = flask_login.current_user
    if loggedin_user.group is None or (group != loggedin_user.group.name):
        g = Group.query.filter(Group.name == group).first()
        # Only request to join the group is the user isn't already in a group
        if flask_login.current_user not in g.join_requests:
            g.join_requests.append(flask_login.current_user)
            db_session.commit()
            flash('Request to join group "{name}" has been submitted.'.format(name=group))
        else:
            flash('Request to join group "{name}" has already been submitted.'.format(name=group))
        return redirect(url_for('groups', group=group))


@app.route('/', methods=['GET'])
@flask_login.login_required
def home():
    PER_PAGE = 25
    q = get_similar_reports(return_query=True)
    if flask_login.current_user.group:
        form = SearchReportsForm()
        if request.args:
            reports = q.filter(CrashReport.group == flask_login.current_user.group,
                               getattr(CrashReport, request.args['field']).contains(str(request.args['value'])))
        else:
            reports = q.filter(CrashReport.group == flask_login.current_user.group)
        reports = reports.all()

        n_total_reports = len(reports)
        max_page = int(ceil(n_total_reports / float(PER_PAGE)))
        try:
            page = max(1, int(request.args.get('page', 1)))
        except ValueError:
            page = 1
        page_rev = max_page - page + 1
        reports = reports[(page_rev-1) * PER_PAGE: page_rev * PER_PAGE]
        pagination = Pagination(page=page, per_page=PER_PAGE, total=n_total_reports, search=False, record_name='reports')
        html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination,
                               form=form)
        return html
    else:
        return redirect(url_for('groups'))

@app.route('/search', methods=['GET', 'POST'])
@flask_login.login_required
def search():
    form = SearchReportsForm()
    if flask_login.current_user.group and form.validate_on_submit():
        return redirect(url_for('home', **form.data))
    else:
        return redirect(url_for('home'))