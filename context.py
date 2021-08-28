from contextlib import contextmanager


@contextmanager
def patch(obj, *delattrs, **setattrs):
    added = object()
    originals = {}
    try:
        for name in delattrs:
            originals[name] = getattr(obj, name)
            delattr(obj, name)
        for name, value in setattrs.items():
            originals[name] = getattr(obj, name, added)
            setattr(obj, name, value)
        yield
    finally:
        for name, value in originals.items():
            if value is added:
                delattr(obj, name)
            else:
                setattr(obj, name, value)


@contextmanager
def translate_exceptions(exc_types):
    """Re-raise exceptions as different types.

    >>> with translate_exceptions({Exception: ValueError}):
    ...     raise Exception('ayy')
    Traceback (most recent call last):
      ...
    ValueError: ayy

    >>> with translate_exceptions({ValueError: KeyError}):
    ...     raise Exception('nope')
    Traceback (most recent call last):
      ...
    Exception: nope
    """
    try:
        yield
    except tuple(exc_types) as exc:
        raise exc_types[type(exc)](exc) from exc


@contextmanager
def handle(handlers):
    """Handle the specified exceptions with the given functions.

    >>> with handle({Exception: print}):
    ...     raise Exception('ayy')
    ayy

    >>> with handle({ValueError: print}):
    ...     raise Exception('nope')
    Traceback (most recent call last):
      ...
    Exception: nope
    """
    try:
        yield
    except tuple(handlers) as exc:
        handlers[type(exc)](exc)
