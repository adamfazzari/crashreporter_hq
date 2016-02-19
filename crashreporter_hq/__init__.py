__author__ = 'calvin'


from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import flask.ext.login as flask_login

# Mock database / persistence layer

app = Flask(__name__)
app.config.from_object('crashreporter_hq.config')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

db = SQLAlchemy(app)

# @app.teardown_appcontext
# def shutdown_session(exception=None):
#     db_session.remove()

import views, models