from functools import partial, wraps
from inspect import signature


def discard(*args, **kwargs):
    pass


def nop(x):
    return x


def generate(x):
    yield x


def call(obj):
    """Call an object with no arguments."""
    return obj()


def call_with(*args, **kwargs):
    """Call a decorated object with the given arguments."""
    return lambda obj: obj(*args, **kwargs)


def combine(*funcs):
    def multifunc(*args, **kwargs):
        return [func(*args, **kwargs) for func in funcs]
    return multifunc


def only_when(condition):
    """Only apply a decorator if the condition is met.

    This function is designed as a decorator for other decorators
    ("re-decorator", perhaps?). If the given condition evaluates True,
    the decorated function is evaluated as usual, wrapping or replacing
    whatever functions it in turn decorates. If the condition evaluates
    False, though, it replaces the decorated function with a direct call
    to the function it wraps, bypassing evaluation of the decorated
    function altogether.

    This evaluation is only performed once, when the decorated function
    is first created (usually when the module is loaded); afterward, it
    adds zero overhead to the actual evaluation of the function.
    """
    def conditional(decorator):
        def redecorator(function):
            if condition:
                return decorator(function)
            else:
                return function
        return redecorator
    return conditional


only_when.csvoss_edition = lambda condition: (
    (lambda decorator: lambda function: decorator(function))
    if condition else
    (lambda decorator: lambda function: function)
)


def wrap(before=None, after=None, ex=None):
    """Apply additional functions before and afterward."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):

            mutable_args = list(args)
            if before:
                before(mutable_args, kwargs)
            try:
                result = func(*mutable_args, **kwargs)
            except Exception as exception:
                if ex:
                    return ex(exception, mutable_args, kwargs)
                else:
                    raise
            else:
                if after:
                    result = after(result, mutable_args, kwargs)
            return result

        return wrapper
    return decorator


def debug(before=None, after=None):
    """Apply additional functions, unless compiled with -O."""
    if not __debug__:
        return nop
    return wrap(before, after)


def curried(func, *, missing_args_template="{.__name__}() missing "):
    """Return partials of ``func`` until all required args have been provided.

    >>> @curried
    ... def cat(a, b, c=3):
    ...     for arg in (a, b, c):
    ...         print(arg, end='')
    ...     print()

    >>> cat(1)(2)
    123
    >>> cat(1, 2)
    123
    >>> cat(c='c')(1)(2)
    12c
    >>> cat(1, 2, 'c')
    12c
    >>> cat(1)(2, 'c')
    12c
    >>> cat(b='b', c='c')(1)
    1bc
    >>> cat(b='b')(1)
    1b3
    >>> cat(c=4)(1, 2)
    124

    >>> cat(1)(2, 3, 4)
    Traceback (most recent call last):
      ...
    TypeError: cat() takes from 2 to 3 positional arguments but 4 were given
    """
    wrap = wraps(func)
    missing_args_message = missing_args_template.format(func)

    @wrap
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except TypeError as exc:
            # The interpreter may have raised this TypeError because we
            # called `func` with an invalid signature, but it could also
            # have come from within `func`.
            #
            # In the latter case, the `tb_next` attribute of the
            # exception's traceback will have information for the stack
            # frame of that call; otherwise, it will be None.
            if exc.__traceback__.tb_next is None:
                # The exception came from our call, not within `func`.
                if str(exc).startswith(missing_args_message):
                    # We don't have enough arguments to call `func` yet.
                    # TODO: Does this blow up the stack?
                    return wrap(partial(wrapper, *args, **kwargs))
            # The exception either came from within `func`, or we called
            # it with too many arguments. Let the caller handle it.
            raise
    return wrapper


def somewhat_more_respectably_curried(func):
    """Return partials of ``func`` until all args have been provided.

    >>> @somewhat_more_respectably_curried
    ... def cat(a, b, c=3):
    ...     for arg in (a, b, c):
    ...         print(arg, end='')
    ...     print()

    >>> cat(1)(2)
    123
    >>> cat(1, 2)
    123
    >>> cat(1, 2, 'c')
    12c
    >>> cat(1)(2, 'c')
    12c
    >>> cat(b='b', c='c')(1)
    1bc
    >>> cat(b='b')(1)
    1b3
    >>> cat(c=4)(1, 2)
    124

    >>> cat(1)(2, 3, 4)
    Traceback (most recent call last):
      ...
    TypeError: too many positional arguments
    """
    bind = signature(func).bind
    wrap = wraps(func)

    @wrap
    def wrapper(*args, **kwargs):
        try:
            bind(*args, **kwargs)
        except TypeError as exc:
            if str(exc).startswith('missing'):
                return wrap(partial(wrapper, *args, **kwargs))
            else:
                raise
        return func(*args, **kwargs)
    return wrapper


def pseudocurried(func):
    """
    >>> pseudocurried(print)('ayy')('lmao')()
    ayy lmao
    """
    accumulated_args = []
    accumulated_kwargs = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        if args or kwargs:
            accumulated_args.extend(args)
            accumulated_kwargs.update(kwargs)
            return wrapper
        else:
            return func(*accumulated_args, **accumulated_kwargs)

    return wrapper


def tee(*funcs):
    """
    >>> noted = []
    >>> note = tee(print, noted.append)
    >>> print(note('ayy'), note('lmao'))
    ayy
    lmao
    ayy lmao
    >>> noted
    ['ayy', 'lmao']
    """
    def teed(obj):
        for func in funcs:
            func(obj)
        return obj
    return teed


show = tee(print)


@curried
def inc_by(n, x):
    return x + n


@curried
def dec_by(n, x):
    return x - n


inc = inc_by(1)
dec = dec_by(1)


def compose(*funcs):
    """Define a function as a chained application of other functions.

    Functions are applied from right to left.

    >>> x = compose(show, dec, show, inc, show)(1)
    1
    2
    1
    >>> x
    1

    >>> o = object()
    >>> compose(nop)(o) is o
    True
    >>> compose(nop) is nop
    True
    """
    *rest, first = funcs
    if not rest:
        return first

    def composed(*args, **kwargs):
        value = first(*args, **kwargs)
        for func in reversed(rest):
            value = func(value)
        return value
    return composed


@curried
def call_until(exc, func):
    """Call and yield ``func`` repeatedly until ``exc`` is raised.

    ``exc`` may be an exception type, or a tuple thereof.

    Usage example:

        >>> @list
        ... @call_until(StopIteration)
        ... def L(it=iter(range(3))):
        ...     return next(it)
        >>> L
        [0, 1, 2]
    """
    try:
        while True:
            yield func()
    except exc:
        return


@curried
def do_until(exc, action, default=None):
    """Call ``action`` repeatedly until ``exc`` is raised.

    ``exc`` may be an exception type, or a tuple thereof.

    Returns the last value returned by ``action``, or ``default`` if
    ``action`` raises on its first call.

    Usage example:

        >>> @do_until(StopIteration)
        ... def last(it=iter(range(3))):
        ...     return show(next(it))
        0
        1
        2
        >>> last
        2

        >>> @do_until(ZeroDivisionError, default='lmao')
        ... def ayy():
        ...     return 1/0
        >>> ayy
        'lmao'
    """
    try:
        while True:
            default = action()
    except exc:
        return default
