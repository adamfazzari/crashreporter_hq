
import os


HQ_FOLDER = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(HQ_FOLDER, 'templates')
STATIC_FOLDER = os.path.join(HQ_FOLDER, 'static')
PYGMENTS_CSS_FILE = os.path.join(TEMPLATE_FOLDER, 'syntax.css')
UPLOAD_FOLDER = os.path.join(HQ_FOLDER, 'reports')
if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Cross-Site Request Forgery prevention
WTF_CSRF_ENABLED = True
SECRET_KEY = 'chocolate-sauce'