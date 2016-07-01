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
