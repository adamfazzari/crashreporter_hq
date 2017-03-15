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


__PROFILER_ENABLED__ = False

if __PROFILER_ENABLED__:
    from sqlalchemy import event
    from sqlalchemy.engine import Engine
    import time
    import logging

    logging.basicConfig()
    logger = logging.getLogger("myapp.sqltime")
    logger.setLevel(logging.DEBUG)

    @event.listens_for(Engine, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement,
                              parameters, context, executemany):
        context._query_start_time = time.time()
        logger.debug("Start Query:\n%s" % statement)
        # Modification for StackOverflow answer:
        # Show parameters, which might be too verbose, depending on usage..
        logger.debug("Parameters:\n%r" % (parameters,))


    @event.listens_for(Engine, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement,
                             parameters, context, executemany):
        total = time.time() - context._query_start_time
        logger.debug("Query Complete!")

        # Modification for StackOverflow: times in milliseconds
        logger.debug("Total Time: %.02fms" % (total * 1000))

import views, models