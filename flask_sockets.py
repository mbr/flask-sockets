# -*- coding: utf-8 -*-

from functools import wraps
from flask import request
from werkzeug import LocalProxy


def log_request(self):
    log = self.server.log
    if log:
        if hasattr(log, 'info'):
            log.info(self.format_request() + '\n')
        else:
            log.write(self.format_request() + '\n')


# Monkeys are made for freedom.
try:
    import gevent
    from geventwebsocket.gunicorn.workers import GeventWebSocketWorker as Worker
except ImportError:
    pass

if 'gevent' in locals():
    # Freedom-Patch logger for Gunicorn.
    if hasattr(gevent, 'pywsgi'):
        gevent.pywsgi.WSGIHandler.log_request = log_request


ws = LocalProxy(lambda: request.environ.get('wsgi.websocket', None))


def socket(f):
    @wraps(f)
    def _(*args, **kwargs):
        if ws is None:
            raise RuntimeError('Websocket support not installed')
        rv = f(*args, **kwargs)
        if rv is None:
            return ''  # avoid empty replies and flask exceptions caused by it
        return rv

    return _


class Sockets(object):
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        pass  # nothing


# CLI sugar.
if 'Worker' in locals():
    worker = Worker