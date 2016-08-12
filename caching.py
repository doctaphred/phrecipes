from functools import partial, wraps
import weakref


def memoize(func):
    """Memoize the function according to its args.

    This decorator does not work with kwargs or unhashable args; see
    below for more robust and flexible approaches.

    >>> print = memoize(print)
    >>> print('ayy')
    ayy
    >>> print('ayy')
    >>> print('lmao')
    lmao
    >>> print('ayy', 'lmao')
    ayy lmao)
    """
    cache = {}

    @wraps(func)
    def memoized(*args):
        try:
            return cache[args]
        except KeyError:
            result = func(*args)
            cache[args] = result
            return result
    return memoized


def freeze(*args, **kwargs):
    return args, frozenset(kwargs.items())


def nop(*args, **kwargs):
    """Do nothing."""
    pass


class Singleton(type):
    """
    Copied from the Python Cookbook.

    # Example
    class Spam(metaclass=Singleton):
        def __init__(self):
            print('Creating Spam')
    """
    def __init__(self, *args, **kwargs):
        self.__instance = None
        super().__init__(*args, **kwargs)

    def __call__(self, *args, **kwargs):
        if self.__instance is None:
            self.__instance = super().__call__(*args, **kwargs)
            return self.__instance
        else:
            return self.__instance


class Cached(type):
    """
    Copied from the Python Cookbook.

    # Example
    class Spam(metaclass=Cached):
        def __init__(self, name):
            print('Creating Spam({!r})'.format(name))
            self.name = name
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__cache = weakref.WeakValueDictionary()

    def __call__(self, *args):
        if args in self.__cache:
            return self.__cache[args]
        else:
            obj = super().__call__(*args)
            self.__cache[args] = obj
            return obj


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
    >>> Test(None)
    Traceback (most recent call last):
      ...
    TypeError: object() takes no parameters

    >>> @instance_cached
    ... class Test:
    ...     def __new__(cls, whatever):
    ...         return object.__new__(cls)

    >>> Test(None) is Test(None)
    True
    >>> Test.__new__.__qualname__
    'Test.__new__'
    >>> Test.__init__.__qualname__
    'object.__init__'
    >>> Test()
    Traceback (most recent call last):
      ...
    TypeError: __new__() missing 1 required positional argument: 'whatever'

    >>> @instance_cached
    ... class Test:
    ...     def __init__(self, whatever):
    ...         pass

    >>> Test(None) is Test(None)
    True
    >>> Test.__new__.__qualname__
    'object.__new__'
    >>> Test.__init__.__qualname__
    'Test.__init__'
    >>> Test()
    Traceback (most recent call last):
      ...
    TypeError: __init__() missing 1 required positional argument: 'whatever'

    TODO: handle default arguments.
    """
    # Allow this decorator to work with or without being called
    if cls is None:
        return partial(instance_cached, cache_func=cache_func)

    overridden_new = cls.__new__ is not object.__new__
    overridden_init = cls.__init__ is not object.__init__

    if overridden_init and not overridden_new:
        @wraps(object.__new__)
        def old_new(cls, *args, **kwargs):
            return object.__new__(cls)
    else:
        old_new = cls.__new__

    if overridden_new and not overridden_init:
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
