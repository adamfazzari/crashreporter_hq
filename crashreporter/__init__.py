__version__ = '1.08'

try:
    from crashreporter import CrashReporter
except ImportError:
    pass

from hq import run_hq
