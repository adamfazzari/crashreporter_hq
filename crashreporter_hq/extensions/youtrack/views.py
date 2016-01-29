from flask import redirect, url_for, request
from ... import app
from ...forms import YoutrackSubmitForm
from ...models import CrashReport
from youtrack import Connection


@app.route('/reports/youtrack/<int:report_number>', methods=['POST'])
def youtrack_submit(report_number):
    cr = CrashReport.query.filter(CrashReport.id==report_number).first()
    form = YoutrackSubmitForm()

    if form.validate_on_submit():
        c = Connection(form.data['server'], form.data['assignee'], form.data['password'])
        report_link = url_for('view_report', report_number=report_number)
        desc = form.data['description'] +  "\n{html}" + \
               '''
               <a href={link}>
               <p>
                File: {tb.file} , line {tb.error_line_number}, in module {tb.module}<br>
                        {tb.error_line}
               </p>

               {cr.error_type}: {cr.error_message}
               </a>
               '''.format(cr=cr, link=request.url_root[:-1] + report_link, tb=cr.traceback[-1]) + \
               '\n{html}'
        resp, cont = c.createIssue(form.data['project'], form.data['assignee'], form.data['summary'],
                                   desc)
        return redirect(report_link)
    else:
        return 'Error'