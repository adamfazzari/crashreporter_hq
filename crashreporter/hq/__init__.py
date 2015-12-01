__author__ = 'calvin'


from flask import Flask

app = Flask(__name__)
app.config.from_object('hq.config')

import views