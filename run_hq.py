__author__ = 'calvin'

from crashreporter_hq import app

import getopt
import sys

def usage():

    print "Command line parameters:"
    print " -d      Sets debug"
    print " -h      host ip"
    print " -p      port"
    print " -s      enable profiling"
    print " --help      Display help"


try:
    opts, args = getopt.getopt(sys.argv[1:], "sh:p:d:")
except getopt.GetoptError:
    print "Invalid command line arguments"
    usage()
    sys.exit()

app_kwargs = {'debug': False, 'host': '0.0.0.0', 'port': 5010}
profile = False
for opt, arg in opts:
    if opt == "-d" and arg:
        app_kwargs['debug'] = True
    elif opt == "-p":
        app_kwargs['port'] = int(arg)
    elif opt == "-s":
        profile = True
    elif opt == "-h":
        app_kwargs['host'] = arg
    elif opt == "--help":
        usage()
        sys.exit()

if profile:
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
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[30])

app.run(**app_kwargs)

