from flask.ext.paginate import Pagination
from datetime import datetime
from math import ceil
from sqlalchemy import or_, func

from ..tools import get_similar_reports
from users import *

from ..forms import SearchReportsForm
from ..models import CrashReport, Application
from ..extensions.views import *
from constants import *
import operator

@app.route('/hq', methods=['GET'])
def hq():
    return render_template('hq.html')


@app.route('/', methods=['GET'])
@flask_login.login_required
def view_reports():
    PER_PAGE = 25
    user = flask_login.current_user
    group = user.group
    show_delete = False

    if not group:
        return redirect(url_for('groups'))

    q = get_similar_reports(return_query=True)
    q = q.join(Application).filter(CrashReport.group == group)

    form = SearchReportsForm()
    show_delete = True
    # Filter aliased state
    aliased_state = int(request.args.get('hide_aliased', ANY))
    if aliased_state == NONE:
        q = q.filter(CrashReport.uuid_id.notin_([a.uuid_id for a in group.aliases]))
        form.hide_aliased.data = str(NONE)
    elif aliased_state == ONLY:
        q = q.filter(CrashReport.uuid_id.in_([a.uuid_id for a in group.aliases]))
        form.hide_aliased.data = str(ONLY)

    # Filter released state
    released_state = int(request.args.get('releases_only', ANY))
    if released_state == NONE:
        q = q.filter(Application.is_release == False)
        form.releases_only.data = str(NONE)
    elif released_state == ONLY:
        q = q.filter(Application.is_release == True)
        form.hide_aliased.data = str(ONLY)

    search_fields = [request.args.get('field%d' % (i+1)) for i in xrange(3)]
    search_values = [request.args.get('value%d' % (i+1)) for i in xrange(3)]
    if any(search_values):
        for ii, (field, value) in enumerate(zip(search_fields, search_values)):
            if not value:
                continue
            # Pre-fill the form with the last search
            getattr(form, 'field%d' % (ii+1)).data = field
            getattr(form, 'value%d' % (ii+1)).data = value
            if field == 'user_identifier':
                # Search the user identifiers associated with any aliases that may be part of the search
                conditions = [UUID.user_identifier.contains(a.user_identifier) for a in group.aliases if value in a.alias]
                conditions.append(UUID.user_identifier.contains(value))
                logic_or = or_(*conditions)
                q = q.filter(logic_or).join(UUID)
            elif field == 'date':
                date = datetime.strptime(value, '%d %B %Y').strftime('%Y-%m-%d')
                q = q.filter(func.date(CrashReport.date) == date)
            elif field == 'before_date':
                date = datetime.strptime(value, '%d %B %Y')
                q = q.filter(CrashReport.date <= date)
            elif field == 'after_date':
                date = datetime.strptime(value, '%d %B %Y')
                q = q.filter(CrashReport.date >= date)
            elif field == 'application_name':
                q = q.filter(Application.name.contains(value))
            elif field in ('application_version', 'after_version', 'before_version'):
                v0, v1, v2 = map(int, value.split('.'))
                op = {'application_version': operator.eq,
                      'after_version': operator.ge,
                      'before_version': operator.le}[field]
                q = q.filter(op(Application.version_0, v0),
                             op(Application.version_1, v1),
                             op(Application.version_2, v2))

            else:
                attr = getattr(CrashReport, field)
                q = q.filter(attr.contains(str(value)))

    reports = q.order_by(CrashReport.id.asc()).all()
    n_total_reports = len(reports)

    max_page = int(ceil(n_total_reports / float(PER_PAGE)))
    try:
        page = max(1, int(request.args.get('page', 1)))
    except ValueError:
        page = 1

    search = 'field1' in request.args
    page_rev = max_page - page + 1
    report_numbers = [str(r['Report Number']) for r in reports]
    reports = reports[(page_rev-1) * PER_PAGE: page_rev * PER_PAGE]
    pagination = Pagination(page=page,
                            per_page=PER_PAGE,
                            total=n_total_reports,
                            outer_window=25,
                            inner_window=25,
                            search=search,
                            search_msg='%d Reports found matching your criteria' % n_total_reports,
                            found=n_total_reports,
                            record_name='reports')
    aliases = {a.user_identifier: a.alias for a in group.aliases}
    html = render_template('index.html', reports=reports, user=flask_login.current_user, pagination=pagination,
                           aliases=aliases, form=form, report_numbers=report_numbers, show_delete=show_delete)
    return html


# This search view is needed because there doesn't seem to be a way to get the pagination links to update
# the page number while maintaining the search form.
@app.route('/search', methods=['GET', 'POST'])
@flask_login.login_required
def search():
    form = SearchReportsForm()
    if flask_login.current_user.group and form.validate_on_submit():
        return redirect(url_for('view_reports', **form.data))
    else:
        return redirect(url_for('view_reports'))