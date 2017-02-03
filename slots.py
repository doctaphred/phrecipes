def slotted(*names, **defaults):
    """Convert a class to use slots, with optional default values.

    >>> @slotted('x', a=1, b=2)
    ... class C:
    ...     d = 4

    >>> c = C(b=5)
    >>> c.a
    1
    >>> c.b
    5
    >>> c.d
    4

    >>> c.a = 6
    >>> c.a
    6
    >>> del c.a
    >>> c.a
    Traceback (most recent call last):
      ...
    AttributeError: a

    >>> c.x
    Traceback (most recent call last):
      ...
    AttributeError: x
    >>> c.x = 7
    >>> c.x
    7
    >>> del c.x
    >>> c.x
    Traceback (most recent call last):
      ...
    AttributeError: x

    >>> C(x=8).x
    8

    >>> c.nope = 'negative'
    Traceback (most recent call last):
      ...
    AttributeError: 'C' object has no attribute 'nope'

    >>> vars(c)
    Traceback (most recent call last):
      ...
    TypeError: vars() argument must have __dict__ attribute

    >>> C.x
    <member 'x' of 'C' objects>
    >>> C.a
    <member 'a' of 'C' objects>
    >>> C.d
    4
    """
    def slotsify(cls):

        def __init__(self, **overrides):
            values = self.__defaults__.copy()
            values.update(overrides)
            for name, value in values.items():
                setattr(self, name, value)

        attrs = vars(cls).copy()
        attrs['__slots__'] = names + tuple(defaults)
        attrs['__defaults__'] = defaults
        attrs['__init__'] = __init__

        return type(cls.__name__, (), attrs)

    return slotsify
