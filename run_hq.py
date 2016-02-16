__author__ = 'calvin'

from crashreporter_hq import app

import argparse

parser = argparse.ArgumentParser(description='Crash Reporter HQ.')

parser.add_argument('--host', metavar='host', type=str, default=None, help='Host IP')
parser.add_argument('--port', metavar='port', type=int, default=None, help='Host port')
parser.add_argument('--profile', metavar='profile', type=bool, default=False, help='Enable profiling')
parser.add_argument('--debug', metavar='debug', type=bool, default=False, help='Debug mode')

args = parser.parse_args()

if args.profile:
    """
    This module provides a simple WSGI profiler middleware for finding
    bottlenecks in web application. It uses the profile or cProfile
    module to do the profiling and writes the stats to the stream provided
    To use, run `flask_profiler.py` instead of `app.py`
    see: http://werkzeug.pocoo.org/docs/0.9/contrib/profiler/
    and: http://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-xvi-debugging-testing-and-profiling
    """

    from werkzeug.contrib.profiler import ProfilerMiddleware

    app.config['PROFILE'] = True
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions = [30])
    app.run(args.host, args.port, debug=args.debug)
else:
    app.run(args.host, args.port, debug=args.debug)

