def __getattr__(name):
    """Lazily initialize module attributes!"""
    try:
        init = globals()['_' + name]
    except KeyError as exc:
        raise AttributeError(name) from exc
    globals()[name] = obj = init()
    return obj
