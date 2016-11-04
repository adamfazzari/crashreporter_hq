__author__ = 'calvin'
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from celery import Celery
from flask_mail import Mail
import flask.ext.login as flask_login


app = Flask(__name__)
app.config.from_object('crashreporter_hq.config')


# Initialize Celery
celery = Celery(app.name, broker=app.config['CELERY_BROKER_URL'])
celery.conf.update(app.config)

# Initialize mail manager
mail = Mail(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db = SQLAlchemy(app)

import views, models