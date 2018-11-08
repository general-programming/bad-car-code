from functools import wraps
from os.path import basename, dirname, join
from glob import glob

PACKET_HANDLERS = {}

def packet(packet_id):
    def decorator(f):
        PACKET_HANDLERS[packet_id] = f

        @wraps(f)
        def wrapper(*args, **kwargs):
            return f(*args, **kwargs)

    return decorator

pwd = dirname(__file__)
for x in glob(join(pwd, '*.py')):
    if not x.startswith('__'):
        __import__(basename(x)[:-3], globals(), locals())

__all__ = [
    "packet",
    "PACKET_HANDLERS",
]
