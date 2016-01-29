__author__ = 'calvin'


from flask import Flask
import flask.ext.login as flask_login

from .database import db_session

# Mock database / persistence layer

app = Flask(__name__)
app.config.from_object('crashreporter_hq.config')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

import views