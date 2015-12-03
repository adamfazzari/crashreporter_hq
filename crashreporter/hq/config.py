
import os


HQ_FOLDER = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(HQ_FOLDER, 'templates')
STATIC_FOLDER = os.path.join(HQ_FOLDER, 'static')
PYGMENTS_CSS_FILE = os.path.join(TEMPLATE_FOLDER, 'syntax.css')
UPLOAD_FOLDER = os.path.join(HQ_FOLDER, 'reports')
TMP_FOLDER = os.path.join(HQ_FOLDER, 'tmp')

DB_ABSOLUTE_PATH = 'sqlite:///' + os.path.join(HQ_FOLDER, 'tmp/users.db')

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

if not os.path.isdir(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)

# Cross-Site Request Forgery prevention
WTF_CSRF_ENABLED = True
SECRET_KEY = 'chocolate-sauce'