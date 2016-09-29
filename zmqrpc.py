import traceback
from datetime import datetime
from itertools import count

import zmq


def serve(procs, port=None, addr='tcp://*', context=None, debug=False):
    """Make some procedures available for remote calls via ØMQ."""
    if context is None:
        context = zmq.Context.instance()

    with context.socket(zmq.REP) as socket:

        if port is None:
            port = socket.bind_to_random_port(addr)
        else:
            socket.bind('{}:{}'.format(addr, port))

        print('Serving at {}:{}'.format(addr, port))
        print('sending and receiving JSON')

        for i in count(1):
            idle = datetime.now()
            print('{}: waiting for request #{}...'.format(idle, i))
            message = socket.poll()
            start = datetime.now()
            print('{}: received request #{} after {}'
                  .format(start, i, start - idle))
            try:
                request = socket.recv_json()
                name, *args = request
                result = procs[name](*args)
                reply = {'result': result}
                print(reply)
                socket.send_json(reply)
            except Exception as exc:
                if debug:
                    traceback.print_exc()
                message = '{}: {}'.format(exc.__class__.__name__, exc)
                reply = {'error': message}
                print(reply)
                socket.send_json(reply)
            end = datetime.now()
            print('{}: replied to #{} after {}'
                  .format(end, i, end - start))


if __name__ == '__main__':
    data = {}
    procs = {
        'GET': data.__getitem__,
        'SET': data.__setitem__,
        'DEL': data.__delitem__,
    }
    serve(procs, 6379)  # Look Ma, Redis!
