#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Standalone probe for the risk-monitor Redis pub/sub feed.

Purpose
-------
Answer one question with hard evidence: **is the service missing data because of
the subscriber, or because nothing is being published?**

It deliberately does NOT import anything from the project (no LogEngine, no
DataService) so it cannot fail for unrelated reasons. It reads the same
``config/dataservice.ini`` and talks to the same Redis with the same channel
names as the service.

Usage
-----
    python3 tools/check_redis_sub.py                 # run until Ctrl-C
    python3 tools/check_redis_sub.py --seconds 60    # stop after 60s
    python3 tools/check_redis_sub.py --raw           # print every raw reply

What to look for
----------------
* ``[b'subscribe', ...]`` lines        -> subscription confirmations, NOT data.
                                          Seeing these more than once means the
                                          client re-subscribed (i.e. reconnected).
* ``[b'message', b'<channel>', ...]``  -> real payload. If these never appear
                                          while this probe is attached, the
                                          problem is on the *publisher* side.
* ``unexpected reply type``            -> the reply shape is neither the raw
                                          list of redis-py 2.x nor the dict of
                                          redis-py 3.x+.
"""

import argparse
import configparser
import json
import os
import sys
import time

try:
    import redis
except ImportError:
    sys.exit('the `redis` package is not installed for this interpreter '
             '(try: python3 -m pip install redis)')


CONFIG_REL = os.path.join('config', 'dataservice.ini')


def load_config():
    here = os.path.dirname(os.path.abspath(__file__))
    candidates = [
        os.path.join(os.path.dirname(here), CONFIG_REL),  # <project>/config/...
        os.path.join(here, CONFIG_REL),
    ]
    for path in candidates:
        if os.path.exists(path):
            cfg = configparser.ConfigParser()
            cfg.read(path)
            return path, cfg
    sys.exit('config/dataservice.ini not found, looked in: %s' % candidates)


def classify(data):
    """Return (kind, channel, payload) for both redis-py reply shapes.

    redis-py 2.x : PubSub.parse_response() returns the RAW reply, e.g.
                   [b'message', b'RMPhysicalAccount', b'{...}']
                   [b'subscribe', b'RMPhysicalAccount', 1]
    redis-py 3.x+: returns a dict, e.g.
                   {'type': 'message', 'channel': b'..', 'data': b'..'}
    """
    if isinstance(data, dict):
        return str(data.get('type')), data.get('channel'), data.get('data')
    if isinstance(data, (list, tuple)) and len(data) >= 3:
        kind = data[0]
        if isinstance(kind, bytes):
            kind = kind.decode('utf-8', 'ignore')
        return str(kind), data[1], data[2]
    return None, None, None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--seconds', type=float, default=0,
                    help='stop after N seconds (0 = run forever)')
    ap.add_argument('--raw', action='store_true',
                    help='print every raw reply, including confirmations')
    args = ap.parse_args()

    path, cfg = load_config()
    host = cfg.get('Redis', 'host')
    port = cfg.get('Redis', 'port')
    password = cfg.get('Redis', 'password') if cfg.has_option('Redis', 'password') else ''
    ch_physical = cfg.get('Redis', 'physicalpubchannel')
    ch_overview = cfg.get('Redis', 'overviewpubchannel')

    print('=' * 72)
    print('config file      : %s' % path)
    print('redis            : %s:%s' % (host, port))
    print('physical channel : %s' % ch_physical)
    print('overview channel : %s' % ch_overview)
    print('redis-py version : %s' % getattr(redis, '__version__', 'unknown'))
    print('=' * 72)

    kwargs = dict(host=host, port=int(port), socket_connect_timeout=5,
                  socket_timeout=30, socket_keepalive=True)
    if password:
        kwargs['password'] = password
    client = redis.StrictRedis(**kwargs)

    # --- sanity checks on a plain (non-pubsub) connection -------------------
    try:
        print('PING             : %s' % client.ping())
    except Exception as exc:
        sys.exit('cannot talk to redis at %s:%s -> %r' % (host, port, exc))

    try:
        n_subs = client.execute_command('PUBSUB', 'NUMSUB', ch_physical, ch_overview)
        print('PUBSUB NUMSUB    : %s   (subscriber counts for the two channels)' % (n_subs,))
        print('PUBSUB CHANNELS  : %s' % (client.execute_command('PUBSUB', 'CHANNELS'),))
    except Exception as exc:
        print('PUBSUB introspection failed: %r' % (exc,))

    pubsub = client.pubsub()
    pubsub.subscribe(ch_physical)
    pubsub.subscribe(ch_overview)

    print('-' * 72)
    print('attached. To prove whether the monitor is publishing at all, run in '
          'another shell:')
    print('    redis-cli -h %s -p %s -a \'<password>\' MONITOR | grep PUBLISH'
          % (host, port))
    print('-' * 72)

    stats = {}
    payloads = 0
    started = time.time()
    last_payload = None
    last_summary = started

    while True:
        if args.seconds and (time.time() - started) > args.seconds:
            break
        try:
            data = pubsub.parse_response()
        except Exception as exc:
            print('[%s] !! parse_response raised %s: %r  (this is what makes the '
                  'service reconnect)' % (time.strftime('%H:%M:%S'),
                                          type(exc).__name__, exc))
            time.sleep(1)
            try:
                pubsub = client.pubsub()
                pubsub.subscribe(ch_physical)
                pubsub.subscribe(ch_overview)
            except Exception as inner:
                print('   reconnect failed: %r' % (inner,))
            continue

        if not data:
            continue

        kind, channel, body = classify(data)
        stats[kind] = stats.get(kind, 0) + 1

        if args.raw or kind not in ('subscribe', 'unsubscribe', 'psubscribe',
                                    'punsubscribe', 'pong'):
            print('[%s] %-10s %-28s %s' % (time.strftime('%H:%M:%S'), kind,
                                           channel,
                                           repr(body)[:160]))

        if kind == 'message':
            payloads += 1
            last_payload = time.time()
            try:
                parsed = json.loads(body.decode('utf-8'))
                print('            -> json ok, type=%r, keys=%s'
                      % (parsed.get('type'), sorted(parsed.keys())[:12]))
            except Exception as exc:
                print('            -> NOT json (%r); first 200 bytes: %r'
                      % (exc, body[:200]))

        if time.time() - last_summary >= 15:
            last_summary = time.time()
            idle = 'never' if last_payload is None else '%.1fs ago' % (time.time() - last_payload)
            print('--- summary: %s | payloads=%d | last payload %s'
                  % (stats, payloads, idle))

    print('=' * 72)
    print('reply type counts : %s' % stats)
    print('payloads received : %d' % payloads)
    if payloads == 0:
        print('VERDICT: this probe received ZERO data messages. The subscriber '
              'code is not the (only) problem -- check the publisher '
              '(redis-cli MONITOR / monitor logs).')
    else:
        print('VERDICT: data DOES arrive on these channels. The service was '
              'losing it in receive_redis_msg() (see the reconnect loop).')


if __name__ == '__main__':
    main()
