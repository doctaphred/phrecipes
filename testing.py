from functools import wraps


def passthrough(x):
    return x


def raises(*allowed_types):
    """Document and enforce all possible exceptions a function might raise.

    All other exceptions raised by the decorated functions are replaced
    with AssertionErrors. This avoids masking the error if an
    inappropriate exception type is caught at a higher level. (Your code
    *never* handles AssertionErrors... *right*?)

    Since this functionality relies on assertions, the decorator is
    replaced with a zero-overhead passthrough if assertions are
    disabled.
    """
    if not __debug__:
        return passthrough

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except BaseException as exc:  # Gotta catch 'em all
                assert isinstance(exc, allowed_types), type(exc)
                raise
        return wrapper
    return decorator
