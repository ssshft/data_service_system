#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Production entry point for dataservice_server.

Why this file exists
--------------------
1. ``run.sh`` has always called ``run.py``, which did not exist -- the service
   could only be started by running ``dataservice_server.py`` directly.
2. ``gevent.monkey.patch_all()`` must run before *any* module that creates a
   socket is imported (Flask, the MySQL driver, redis).  Doing it here, first, is
   the correct place, and in gevent mode it is a documented requirement: without
   it, blocking calls inside request handlers (the MySQL queries on
   /get_* routes) stall the whole event loop, Socket.IO clients hit their ping
   timeout, and they abort requests -- which is one of the causes of the
   'post request handler error' noise below.
3. It installs a narrow logging filter for that noise (see next section).

The error being silenced
------------------------
    post request handler error
    ...
    OSError: unexpected end of file while reading request at position 0

That happens when a browser aborts a Socket.IO long-poll POST (tab closed,
navigation, refresh, network drop): the request line and headers arrive, the body
never does, and gevent's ``WSGIInput.read()`` raises while python-engineio is
reading the body.

It is **not fatal**.  python-engineio's POST branch is:

    try:
        socket.handle_post_request(environ)
        r = self._ok(jsonp_index=jsonp_index)
    except exceptions.EngineIOError:
        ...
    except:                                        # <- this one
        self.logger.exception('post request handler error')
        r = self._ok(jsonp_index=jsonp_index)      # still answers 200

The exception is swallowed and a 200 is returned; the service keeps running.
Only the ERROR-level traceback is unwanted.

Note: this *cannot* be fixed from gevent's side.  gevent catches the exception
inside ``handle_one_response()`` (it logs "<request> failed with OSError" itself),
so overriding ``WSGIHandler.handle_one_request`` / ``handle_error`` never sees it
-- verified experimentally.  The traceback the user sees comes from engineio, so
the only two levers are (a) stop the client from aborting (patch_all +
gevent-websocket, below) and (b) filter engineio's log record.

Usage
-----
    python3 run.py                       # 0.0.0.0:8020
    python3 run.py --port 9000
    python3 run.py --keep-abort-logs     # keep the full traceback
    ./run.sh                             # same as `python3 run.py`
"""

import argparse
import logging
import os
import sys

# --- must come before anything that imports socket / threading / time ---------
from gevent import monkey
monkey.patch_all()
# -----------------------------------------------------------------------------

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

ABORTED_POST_MESSAGE = 'post request handler error'


class _CondenseAbortedPostLog(logging.Filter):
    """Turn engineio's aborted-POST traceback into a one-line notice.

    engineio logs the traceback with ``logger.exception()``; ``record.msg`` is
    exactly ``'post request handler error'``.  Anything else passes through
    untouched, so real engineio errors are still reported in full.
    """

    def filter(self, record):
        if record.getMessage() != ABORTED_POST_MESSAGE:
            return True
        exc = record.exc_info[1] if record.exc_info else None
        print('[run.py] dropped an aborted request from the client: %s: %s'
              % (type(exc).__name__, exc) if exc is not None
              else '[run.py] dropped an aborted request from the client')
        return False


def install_aborted_post_filter():
    """Attach the filter where engineio actually logs from.

    ``Server.__init__`` does ``self.logger = logging.getLogger('engineio.server')``
    and logs directly through it, so a logger-level filter is effective there.
    The same filter is also attached to the root handlers as a safety net for
    engineio versions that log through a child logger.
    """
    f = _CondenseAbortedPostLog()
    logging.getLogger('engineio.server').addFilter(f)
    for handler in logging.getLogger().handlers:
        handler.addFilter(f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--host', default='0.0.0.0')
    ap.add_argument('--port', type=int, default=8020)
    ap.add_argument('--access-log', action='store_true',
                    help='let gevent log every request (off by default)')
    ap.add_argument('--keep-abort-logs', action='store_true',
                    help='do not filter the aborted-POST traceback')
    args = ap.parse_args()

    # Importing the app also constructs DataService (MySQL + redis pubsub), so this
    # must happen after monkey.patch_all() above.
    from dataservice_server import app, socketio

    if not args.keep_abort_logs:
        install_aborted_post_filter()

    try:
        import geventwebsocket  # noqa: F401
    except ImportError:
        print('[run.py] gevent-websocket is not installed, so Socket.IO clients '
              'cannot upgrade to WebSocket and stay on long-polling -- which makes '
              'aborted POSTs (and this log noise) more likely. '
              'Install it with: python3 -m pip install gevent-websocket')

    print('[run.py] serving on %s:%d (async_mode=%s)'
          % (args.host, args.port, socketio.async_mode))
    try:
        socketio.run(app, host=args.host, port=args.port,
                     log_output=args.access_log)
    except KeyboardInterrupt:
        print('[run.py] shutting down')


if __name__ == '__main__':
    main()
