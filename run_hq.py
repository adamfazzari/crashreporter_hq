__author__ = 'calvin'

from crashreporter_hq import app

import argparse

parser = argparse.ArgumentParser(description='Crash Reporter HQ.')

parser.add_argument('--host', metavar='host', type=str, default=None, help='Host IP')
parser.add_argument('--port', metavar='port', type=int, default=None, help='Host port')
parser.add_argument('--debug', metavar='debug', type=bool, default=False, help='Debug mode')

args = parser.parse_args()


app.run(args.host, args.port, debug=args.debug)