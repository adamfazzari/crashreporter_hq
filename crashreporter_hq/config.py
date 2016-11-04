
import os


HQ_FOLDER = os.path.dirname(os.path.realpath(__file__))
TEMPLATE_FOLDER = os.path.join(HQ_FOLDER, 'templates')
STATIC_FOLDER = os.path.join(HQ_FOLDER, 'static')
PYGMENTS_CSS_FILE = os.path.join(TEMPLATE_FOLDER, 'syntax.css')
TMP_FOLDER = os.path.join(HQ_FOLDER, 'tmp')

DB_ABSOLUTE_PATH = os.path.join(HQ_FOLDER, 'tmp/database.db')

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + DB_ABSOLUTE_PATH
SQLALCHEMY_MIGRATE_REPO = os.path.join(HQ_FOLDER, 'db_repository')


# Redis
REDIS_URL = 'redis://127.0.0.1:6379/0'

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

# Flask-Mail

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 587
MAIL_USE_TLS = True
MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
MAIL_DEFAULT_SENDER = 'flask@example.com'


if not os.path.isdir(TMP_FOLDER):
    os.makedirs(TMP_FOLDER)

# Cross-Site Request Forgery prevention
WTF_CSRF_ENABLED = True
SECRET_KEY = 'chocolate-sauce'