from datetime import datetime
from functools import wraps


def timed(func):
    """Make func also return its execution time and any exception raised.
    The return value of the wrapped function is a 3-tuple:
    (result, time, exception), where:
        - result is the returned value of the function (or None if
          an exception was raised),
        - time is the time spent in the function call,
        - exception is any exception raised, or None if the function
          returned normally.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            result = None
            exception = e
        else:
            exception = None
        end = datetime.now()
        return result, end - start, exception
    return wrapper
