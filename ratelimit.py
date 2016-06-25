from collections import deque
from functools import wraps
import time


class RateLimiter:
    """
    >>> from unittest.mock import Mock
    >>> from itertools import count

    >>> func = Mock()
    >>> clock = count().__next__
    >>> limited = RateLimiter(1, 1, func, clock=clock)

    >>> len(limited.times_called)
    0
    >>> limited.below_limit()
    True
    >>> func.call_count
    0

    >>> _ = limited()
    >>> len(limited.times_called)
    1
    >>> limited.below_limit()
    False
    >>> func.call_count
    1

    >>> _ = limited()
    >>> len(limited.times_called)
    1
    >>> limited.below_limit()
    False
    >>> func.call_count
    2
    """

    def __init__(self, calls_per_interval, interval, func,
                 fallback=None, clock=time.perf_counter):
        self.calls_per_interval = calls_per_interval
        self.times_called = deque(maxlen=calls_per_interval)
        self.interval = interval
        self.func = func
        self.fallback = fallback
        self.clock = clock

    def below_limit(self):
        if len(self.times_called) < self.calls_per_interval:
            return True
        return self.clock() - self.times_called[-1] > self.interval

    def __call__(self, *args, **kwargs):
        if self.below_limit():
            self.times_called.append(self.clock())
            return self.func(*args, **kwargs)
        elif self.fallback is not None:
            return self.fallback(*args, **kwargs)
        else:
            return None


def rate_limit(calls_per_interval, interval, **kwargs):
    def decorator(func):
        return wraps(func)(RateLimiter(
            calls_per_interval, interval, func, **kwargs).__call__)
    return decorator
