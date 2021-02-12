def __getattr__(name):
    """Lazily initialize module attributes!"""
    globals()[name] = obj = globals()['_' + name]()
    return obj
