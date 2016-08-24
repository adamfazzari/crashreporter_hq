from flask.ext.paginate import Pagination
from datetime import datetime
from math import ceil
from sqlalchemy import or_

from ..tools import get_similar_reports
from users import *

from ..forms import SearchReportsForm
from ..models import CrashReport
from ..extensions.views import *


@app.route('/', methods=['GET'])
@flask_login.login_required
def home():
    PER_PAGE = 25
    q = get_similar_reports(return_query=True)
    if flask_login.current_user.group:
        form = SearchReportsForm()
        search_fields = [request.args.get('field%d' % (i+1)) for i in xrange(3)]
        search_values = [request.args.get('value%d' % (i+1)) for i in xrange(3)]
        if any(search_values):
            for field, value in zip(search_fields, search_values):
                if not value:
                    continue

                if field == 'user_identifier':
                    # Search the user identifiers associated with any aliases that may be part of the search
                    logic_or = or_(UUID.user_identifier.contains(a.user_identifier) for a in flask_login.current_user.group.aliases if value in a.alias)
                    q = q.filter(CrashReport.group == flask_login.current_user.group, logic_or).join(UUID)

                elif field == 'before_date':
                    date = datetime.strptime(value, '%d %B %Y')
                    q = q.filter(CrashReport.group == flask_login.current_user.group,
                            CrashReport.date <= date)
                elif field == 'after_date':
                    date = datetime.strptime(value, '%d %B %Y')
                    q = q.filter(CrashReport.group == flask_login.current_user.group,
                                 CrashReport.date >= date)

                else:
                    attr = getattr(CrashReport, field)
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


@app.route('/search', methods=['GET', 'POST'])
@flask_login.login_required
def search():
    form = SearchReportsForm()
    if flask_login.current_user.group and form.validate_on_submit():
        return redirect(url_for('home', **form.data))
    else:
        return redirect(url_for('home'))