from functools import partial, wraps
import weakref


def freeze(*args, **kwargs):
    return args, frozenset(kwargs.items())


def nop(*args, **kwargs):
    """Do nothing."""
    pass


def weak_cached(func=None, *, key_func=freeze):
    """Cache the function's return values with weak references.

    Once the decorated function has been called with a given set of args
    and kwargs, it will return the same object for all subsequent calls,
    as long as another non-weak reference to the object still exists.

    This decorator may be applied directly, or may be called in order to
    specify `key_func`, which is called to determine a cache key from a
    given set of args and kwargs. The default function will not work if
    `args` or `kwargs` contain any unhashable values.
    """
    # Allow this decorator to work with or without being called
    if func is None:
        return partial(weak_cached, key_func=key_func)

    cache = weakref.WeakValueDictionary()

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = key_func(*args, **kwargs)
        try:
            return cache[key]
        except KeyError:
            cache[key] = result = func(*args, **kwargs)
            return result

    wrapper._cache = cache
    wrapper._cache_key = key_func
    return wrapper


class WeakCached(type):
    __call__ = weak_cached(type.__call__)


def instance_cached(cls=None, *, cache_func=weak_cached):
    """Decorator to cache a class' instances.

    >>> @instance_cached
    ... class Test:
    ...     def __new__(cls, value):
    ...         print('__new__', value)
    ...         return object.__new__(cls)
    ...     def __init__(self, value):
    ...         print('__init__', value)
    ...         self.value = value

    tl;dr: constructors with the same arguments return the same object:

    >>> Test(1) is Test(1)
    __new__ 1
    __init__ 1
    True

    The default cache function, `weak_cached`, only holds each value as
    long as another non-weak reference to it remains.

    As long as a reference persists, neither __new__ nor __init__ is
    called twice for the same set of arguments: the constructor returns
    a cached instance instead.

    >>> t = Test(1)
    __new__ 1
    __init__ 1
    >>> t is Test(1)
    True
    >>> Test(1) is Test(1)
    True
    >>> Test(1) is Test(2)
    __new__ 2
    __init__ 2
    False

    Cached instances are deleted when no more references remain, and
    subsequent constructor calls execute normally:

    >>> del t
    >>> Test(1) is Test(1)
    __new__ 1
    __init__ 1
    True

    Names, docstrings, etc. are unaffected:

    >>> Test.__new__.__qualname__
    'Test.__new__'
    >>> Test.__init__.__qualname__
    'Test.__init__'

    Also works for classes that don't override __new__ or __init__:

    >>> @instance_cached
    ... class Test:
    ...     pass

    >>> Test() is Test()
    True
    >>> Test.__new__.__qualname__
    'object.__new__'
    >>> Test.__init__.__qualname__
    'object.__init__'

    TODO: make the new constructor's signature match the original.
    (This section of doctests should fail to execute.)

    >>> Test(1) is Test(1)
    True
    >>> t = Test(1)
    >>> t is Test(1)
    True
    >>> Test(1) is Test(1)
    True
    >>> Test(1) is Test(2)
    False
    >>> del t
    >>> Test(1) is Test(1)
    True

    Can be used with other caching functions, which may behave differently:

    >>> from functools import lru_cache
    >>> @instance_cached(cache_func=lru_cache(maxsize=1))
    ... class Test:
    ...     def __new__(cls, value):
    ...         print('__new__', value)
    ...         return object.__new__(cls)
    ...     def __init__(self, value):
    ...         print('__init__', value)
    ...         self.value = value

    >>> Test(1) is Test(1)
    __new__ 1
    __init__ 1
    True
    >>> t = Test(1)  # The LRU cache persists...
    >>> t is Test(1)
    True
    >>> t2 = Test(2)
    __new__ 2
    __init__ 2
    >>> Test(1) is Test(2)  # ...but, it can only remember a single item.
    __new__ 1
    __init__ 1
    __new__ 2
    __init__ 2
    False

    TODO: handle default arguments.
    """
    # Allow this decorator to work with or without being called
    if cls is None:
        return partial(instance_cached, cache_func=cache_func)

    if cls.__new__ is object.__new__:
        # object.__new__ only accepts the single cls argument
        @wraps(object.__new__)
        def old_new(cls, *args, **kwargs):
            return object.__new__(cls)
    else:
        old_new = cls.__new__

    if cls.__init__ is object.__init__:
        # object.__init__ only accepts the single self argument
        @wraps(object.__init__)
        def old_init(self, *args, **kwargs):
            return object.__init__(self)
    else:
        old_init = cls.__init__

    @cache_func
    @wraps(old_new)
    def new_new(cls, *args, **kwargs):
        new_obj = old_new(cls, *args, **kwargs)
        old_init(new_obj, *args, **kwargs)
        return new_obj

    cls.__new__ = new_new
    # __init__ is always invoked after __new__:
    # make sure it has no effect
    cls.__init__ = wraps(old_init)(nop)

    return cls
