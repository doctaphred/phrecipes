from functools import partial


class join:
    r"""Wrap a generator with str.join.

        >>> @join.on('\n')
        ... def lines(**kwargs):
        ...     for k, v in kwargs.items():
        ...         yield f'{k}={v}'
        >>> print(lines(foo='bar', ayy='lmao'))
        foo=bar
        ayy=lmao

    Automatically coerces yielded values to strings:

        >>> join(range)(10)
        '0123456789'

    Also works as a method decorator:

        >>> class Fancy(dict):
        ...     @join.on('\n')
        ...     def __repr__(self):
        ...         yield type(self).__name__
        ...         for name, value in self.items():
        ...             yield f'  {name}: {value}'

        >>> Fancy(a=1, b=2)
        Fancy
          a: 1
          b: 2

    """
    def __init__(self, func, sep=''):
        self.func = func
        self.sep = sep

    @classmethod
    def on(cls, sep):
        return partial(cls, sep=sep)

    def __call__(*args, **kwargs):
        self, *args = args
        return self.sep.join(map(str, self.func(*args, **kwargs)))

    def __get__(self, instance, owner):
        """Works as a method decorator too!"""
        return partial(self, instance)
