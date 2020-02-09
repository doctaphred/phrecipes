class Exposed:

    def __init__(self, gen):
        super().__setattr__('_gen', gen)

    def __next__(self):
        gen = super().__getattribute__('_gen')
        return next(gen)

    def __iter__(self):
        return self

    def __getattr__(self, name):
        gen = super().__getattribute__('_gen')
        try:
            return gen.gi_frame.f_locals[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        gen = super().__getattribute__('_gen')
        # Modifying f_locals will not have any effect...
        gen.gi_frame.f_locals[name] = value
        # ...without this:
        import ctypes
        ctypes.pythonapi.PyFrame_LocalsToFast(
            ctypes.py_object(gen.gi_frame),
            ctypes.c_int(0),  # Update names, but don't add new ones.
            # ctypes.c_int(1),  # Update names and add new ones.
        )

    def __dir__(self):
        gen = super().__getattribute__('_gen')
        yield from gen.gi_frame.f_locals.keys()


def expose(generator):
    """
    >>> @expose
    ... def gen():
    ...     i = 0
    ...     while True:
    ...         yield i
    ...         i += 1

    >>> g = gen()
    >>> dir(g)
    []
    >>> next(g)
    0
    >>> dir(g)
    ['i']
    >>> g.i
    0
    >>> next(g)
    1
    >>> g.i
    1
    >>> g.i = 2
    >>> g.i
    2
    >>> next(g)
    3
    """
    def inner(*args, **kwargs):
        return Exposed(generator(*args, **kwargs))
    return inner
