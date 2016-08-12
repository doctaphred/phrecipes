from collections import deque
from functools import partial, wraps
import time


class RateLimited(RuntimeError):
    pass


class RateLimit:

    def __init__(self, max_calls, interval, clock=time.perf_counter):
        self.max_calls = max_calls
        self.interval = interval
        self.clock = clock
        self.calls = deque(maxlen=max_calls)

    def cooldown(self, timestamp=None):
        """Return the remaining time until the rate limit resets."""
        if timestamp is None:
            timestamp = self.clock()

        if len(self.calls) < self.max_calls:
            return 0.0

        current_interval = timestamp - self.calls[-1]
        if current_interval > self.interval:
            return 0.0

        return self.interval - current_interval

    def attempt(self, func, *args, **kwargs):
        """Call the function, or raise RateLimited."""
        timestamp = self.clock()
        cooldown = self.cooldown(timestamp)
        if cooldown:
            raise RateLimited(cooldown)
        self.calls.append(timestamp)
        return func(*args, **kwargs)

    def __call__(self, func):
        """Allow this object to be used as a function wrapper or decorator."""
        return wraps(func)(partial(self.attempt, func))
