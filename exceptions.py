from functools import wraps


def raise_(exc):
    raise exc


def unique_exception(name):
    """Create a unique subclass of BaseException.

    Usage example:

        >>> try:
        ...     raise unique_exception('ayy')('lmao')
        ... except unique_exception('ayy'):
        ...     print("didn't read lol")
        Traceback (most recent call last):
          ...
        exceptions.ayy: lmao

    """
    return type(name, (BaseException,), {})


def raises(*allowed, base=Exception, otherwise=None):
    """Document and enforce all exceptions a function might raise.

    All other exceptions raised by the decorated functions are
    replaced with AssertionErrors, which should

    avoids masking the error if
    an inappropriate exception type is caught at a higher level.

    The decorator is replaced with a zero-overhead passthrough if
    assertions are disabled.

    Usage example:

        >>> @raises(ArithmeticError)
        ... def f(x):
        ...     return (x ** x) / x

    Exceptions of the allowed types raise normally:

        >>> f(0)
        Traceback (most recent call last):
          ...
        ZeroDivisionError: division by zero

        >>> import sys; f(sys.float_info.max)  # doctest: +ELLIPSIS
        Traceback (most recent call last):
          ...
        OverflowError: (...)

    Others are converted into (mostly) uncatchable types:

        >>> try:  # doctest: +ELLIPSIS
        ...     f('ayy')
        ... except Exception:
        ...     pass
        Traceback (most recent call last):
          ...
        exceptions.UnexpectedException: TypeError: unsupported...

    """
    if not __debug__:
        return lambda func: func
    else:

        for exc_type in allowed:
            if not issubclass(exc_type, base) or exc_type == base:
                raise ValueError(
                    f"allowed exceptions must inherit from the given"
                    f" base class ({base.__name__});"
                    f" {exc_type.__name__} does not"
                )

        if otherwise is None:
            otherwise = unique_exception('UnexpectedException')

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                try:
                    func(*args, **kwargs)
                except allowed:
                    raise
                except base as exc:
                    msg = type(exc).__name__
                    if exc.args:
                        msg = f"{msg}: {exc}"
                    raise otherwise(msg) from exc
            return wrapper
        return decorator
