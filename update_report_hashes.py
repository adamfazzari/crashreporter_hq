
from crashreporter_hq import db
from crashreporter_hq.models import CrashReport, Traceback


def update_related_report_hashes():

    reports = db.session.query(CrashReport).all()

    for r in reports:
        r.related_group_id = CrashReport.get_related_hash(r)

    related_report_hashes = db.session.query(CrashReport.related_group_id).distinct().all()
    for (related_hash, ) in related_report_hashes:
        related_reports = db.session.query(CrashReport).filter(CrashReport.related_group_id == related_hash).all()
        for r in related_reports:
            r.related_reports = related_reports

    db.session.commit()


update_related_report_hashes()