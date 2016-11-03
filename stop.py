from contextlib import contextmanager
from unittest.mock import patch


def stop():
    """Immediately halt execution of the code under test.

    Useful for reducing the duration of integration tests and the risk
    of side effects from irrelevant code.

    Each call to this function returns a unique class which may be
    specifically caught, without interfering with other simultaneous
    uses.
    """
    return type('Stop', (BaseException,), {})


@contextmanager
def stop_at(target):
    exc = stop()
    with patch(target, side_effect=exc()):
        try:
            yield
        except exc:
            pass


@contextmanager
def assert_called(target):
    exc = stop()
    with patch(target, side_effect=exc()):
        try:
            yield
        except exc:
            pass
        raise AssertionError('{} was not called'.format(target))


@contextmanager
def assert_not_called(target):
    exc = stop()
    with patch(target, side_effect=exc()):
        try:
            yield
        except exc:
            raise AssertionError('{} was called'.format(target))
