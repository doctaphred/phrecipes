class Exposed:

    def __init__(self, gen):
        self.__gen = gen

    def __next__(self):
        return next(self.__gen)

    def __iter__(self):
        return self

    def __getattr__(self, name):
        try:
            return self.__gen.gi_frame.f_locals[name]
        except KeyError:
            raise AttributeError(name)

    def __dir__(self):
        # yield from super().__dir__()
        yield from self.__gen.gi_frame.f_locals.keys()


def expose(generator):
    """
    >>> @expose
    ... def gen():
    ...     for i in range(10):
    ...         yield i

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
    """
    def inner(*args, **kwargs):
        return Exposed(generator(*args, **kwargs))
    return inner
