__version__ = '1.08'

try:
    from crashreporter import CrashReporter
except ImportError as e:
    print e
