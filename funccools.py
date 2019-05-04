from functools import partial, wraps
from inspect import signature


def nop(*args, **kwargs):
    pass


def passthrough(x):
    return x


def generate(x):
    yield x


def call_with(*args, **kwargs):
    def decorator(callable, *, args=args, kwargs=kwargs):
        return callable(*args, **kwargs)
    return decorator


call = call_with()


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
        return passthrough
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
            if exc.__traceback__.tb_next is None:
                # The exception came from our call, not the function.
                if str(exc).startswith(missing_args_message):
                    return wrap(partial(wrapper, *args, **kwargs))
            # The exception either came from within the function, or
            # represents too many arguments.
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

    >>> def show(x):
    ...    print(x)
    ...    return x

    >>> x = compose(show, dec, show, inc, show)(1)
    1
    2
    1
    >>> x
    1

    >>> o = object()
    >>> compose(passthrough)(o) is o
    True
    >>> compose(passthrough) is passthrough
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
