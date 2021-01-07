from functools import partial


class Karen:
    """Wants to speak to a context manager.

    >>> file = partial(Karen, open)
    >>> file('ayy.txt', 'w').write('lmao')
    4
    >>> file('ayy.txt', 'r').read()
    'lmao'
    """

    def __init__(self, manager, /, *args, **kwargs):
        self._manager = manager
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, name):
        def call_method(ctx, *args, **kwargs):
            return getattr(ctx, name)(*args, **kwargs)
        return partial(self, call_method)

    def __call__(self, func, /, *args, **kwargs):
        with self._manager(*self._args, **self._kwargs) as ctx:
            return func(ctx, *args, **kwargs)


file = partial(Karen, open)
