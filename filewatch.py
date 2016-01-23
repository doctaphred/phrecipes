import time
from pathlib import Path
from threading import Thread


def _watch(callback, path, interval):
    path = Path(path)
    last_modified = path.stat().st_mtime
    while True:
        modified = path.stat().st_mtime
        if modified != last_modified:
            callback(modified)
            last_modified = modified
        time.sleep(interval)


def watch(callback, path, interval=0.5):
    """Invoke callback whenever the given file has been modified.

    This operation polls the filesystem, so a minimum interval between
    polls must be given, and should be as large as possible to avoid
    excessive overhead.

    Note that the resolution of modification time varies by OS and
    filesystem: on HFS+, it is 1 second. The minimum effective setting
    for interval is therefore resolution / 2, or 0.5 seconds on HFS+.

    The callback is given a single argument: the modification time in
    seconds.

    Args:
        callback: called every time the specified file is modified.
        path: a path to a file (string or pathlib.Path).
        interval: the minimum interval between filesystem polls, in
            seconds.
    Side effects:
        Starts a daemon thread which may invoke the given callback.
    """
    Thread(target=_watch, args=(callback, path, interval), daemon=True).start()


if __name__ == '__main__':
    import sys
    path = sys.argv[1]

    def time_delta_printer():
        last_modified = yield
        print(path, 'first modified at', last_modified)
        while True:
            modified = yield
            print(path, 'modified after', modified - last_modified, 's')
            last_modified = modified

    printer_coroutine = time_delta_printer()
    next(printer_coroutine)  # Advance the coroutine to the first yield

    watch(printer_coroutine.send, path)
    print('Watching', path)
    print('Press enter to stop')
    input()

    # $ python3 filewatch.py test.txt
    # Watching test.txt
    # Press enter to stop
    # test.txt first modified at 1453569373.0
    # test.txt modified after 1.0 s
    # test.txt modified after 1.0 s
    # test.txt modified after 3.0 s
    # test.txt modified after 1.0 s
    # test.txt modified after 2.0 s
