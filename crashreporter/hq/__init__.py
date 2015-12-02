__author__ = 'calvin'


from flask import Flask
import flask.ext.login as flask_login

# Mock database / persistence layer
users = {'admin': {'password': 'secret'}}

app = Flask(__name__)
app.config.from_object('hq.config')

login_manager = flask_login.LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

import views