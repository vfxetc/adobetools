from metatools.imports import load_entrypoint
from Queue import Queue
import argparse
import datetime
import json
import os
import sys
import threading
import weakref
import traceback


NoResult = object()


def log(msg, *args, **kwargs):
    if args or kwargs:
        msg = msg.format(*args, **kwargs)
    msg = '[adobetools] {} {}\n'.format(datetime.datetime.now().isoformat('T'), msg.strip())
    sys.stderr.write(msg)
    sys.stderr.flush()

def send(msg=None, **kwargs):
    msg = dict(msg or {}).copy()
    msg.update(kwargs)
    encoded = json.dumps(msg, sort_keys=True)
    log('Send: ' + encoded)
    sys.__stdout__.write(encoded + '\n')
    sys.__stdout__.flush()

def reply(src, msg=None, **kwargs):
    msg = dict(msg or {}).copy()
    msg.update(kwargs)
    id_ = src.get('id')
    if id_ is not None:
        msg.setdefault('id', id_)
    send(msg)

def format_exception(e):
    return dict(type='error', error_type=e.__class__.__name__, error=str(e))




_handlers = {}

def register(func):
    name = func.__name__
    if name.startswith('on_'):
        name = name[3:]
    _handlers[name] = func
    return func

@register
def on_hello(**kw):
    kw['type'] = 'elloh'
    return kw
@register
def on_elloh(**kw):
    return NoResult

@register
def on_ping(**kw):
    kw['type'] = 'pong'
    return kw
@register
def on_pong(**kw):
    return NoResult

@register
def on_debug_raise_error(**kw):
    raise ValueError(kw.get('message', 'This is a test.'))

def debug_environ():
    return '\n'.join('{}: {!r}'.format(*x) for x in sorted(os.environ.iteritems()))


_call_count = 0
_call_threads = weakref.WeakValueDictionary()

@register
def on_call(func, args=None, kwargs=None, **msg):

    global _call_count
    _call_count += 1

    thread = _call_threads[_call_count] = threading.Thread(target=_call_thread, args=[msg, func, args, kwargs])
    thread.daemon = True
    thread.message = msg
    thread.start()
    del thread # Kill this reference immediately.

    return NoResult


def _call_thread(msg, entrypoint, args, kwargs):

    log('Calling: {}', entrypoint)

    try:
        func = load_entrypoint(entrypoint, reload=None)
    except Exception as e:
        reply(msg, format_exception(e))
        return

    if not func:
        send(type='error', error='Could not load entrypoint.', detail=entrypoint)
        return

    args = args or ()
    kwargs = kwargs or {}

    try:
        res = func(*args, **kwargs)
    except Exception as e:
        traceback.print_exc()
        reply(msg, format_exception(e))
        return

    if res is NoResult:
        return
    reply(msg, type='result', result=res)


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action='store_true')
    args = parser.parse_args()

    # We need to take over both stdout and stderr so that print statements
    # don't result in Premiere thinking it is getting a message back.
    if args.verbose:
        sys.stdout = sys.stderr
    else:
        sys.stdout = open('/tmp/adobetools-premiere-runtime.log', 'a')
        sys.stderr = sys.stdout

    log('Starting.')

    send(
        type='hello',
        file=__file__,
    )

    while True:

        encoded = sys.stdin.readline()
        if not encoded:
            log('stdin closed.')
            return

        encoded = encoded.strip()
        if not encoded:
            continue

        log('Recv: {}', encoded)

        try:
            msg = json.loads(encoded)
        except ValueError as e:
            send(type='error', error='malformed message', detail='{}: {}'.format(e.__class__.__name__, e))
            continue

        if not isinstance(msg, dict):
            send(type='error', error='malformed message', detail='non-dict')
            continue

        type_ = msg.pop('type', None)
        id_ = msg.get('id')
        if not type_:
            send(type='error', error='malformed message', detail='no type')
            continue

        func = _handlers.get(type_)
        if not func:
            send(type='error', error='unknown message type', detail=type_)
            continue

        try:
            res = func(**msg)
        except Exception as e:
            send(format_exception(e))
            continue
        
        if res is NoResult:
            continue

        if not isinstance(res, dict):
            res = {'value': res}
        res.setdefault('type', 'result')
        res.setdefault('id', id_)
        send(res)
            




if __name__ == '__main__':
    main()
