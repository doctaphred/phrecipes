def enum(*names):
    """
    >>> @enum('a', 'b', 'c')
    ... class Things:
    ...     pass
    >>> Things.a
    (<class 'enums.Things'>, 'a')
    >>> Things.x
    Traceback (most recent call last):
      ...
    AttributeError: x
    """
    names = set(names)

    def enumify(cls):
        def __getattr__(self, name):
            if name in names:
                return cls, name
            raise AttributeError(name)
        cls.__getattr__ = __getattr__
        return cls()

    return enumify
