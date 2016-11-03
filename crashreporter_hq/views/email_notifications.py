from users import *
from ..tasks import send_status_report


@app.route('/start_task', methods=['GET'])
@flask_login.login_required
def start_task():
    task = send_status_report.apply_async(args=[10, 20], countdown=5)
    return 'Done'