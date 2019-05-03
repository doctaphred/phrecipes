from collections import OrderedDict
from functools import partial, wraps
from inspect import signature
import weakref


def basic_memoize(func):
    """Basic implementation, just for reference."""
    cache = {}

    @wraps(func)
    def memoized(*args):
        try:
            return cache[args]
        except KeyError:
            cache[args] = result = func(*args)
        return result

    memoized._cache = cache

    return memoized


def memoize(func=..., *, cache=..., key='received'):
    """Preserve and reuse a function's return values.

    The default cache is a dict. The key may be 'received', 'called',
    'positional', or a custom function which accepts *args and **kwargs.

    If key is 'received' (the default), the cache key uses the arguments
    the memoized function actually receives when called, appropriately
    handling keyword args and default values:

        >>> @memoize
        ... def say(something, also='lmao'):
        ...     print(something, also)
        >>> say('ayy')
        ayy lmao
        >>> say(something='ayy')
        >>> say('ayy', 'lmao')
        >>> say('ayy', also='lmao')
        >>> say(something='ayy', also='lmao')
        >>> say(also='lmao', something='ayy')
        >>> say('ayy', also='waddup')
        ayy waddup

    If key is 'called', the cache key uses the signature the cached
    function is actually called with. This causes calls with different
    signatures to be cached separately, even if they are semantically
    equivalent:

        >>> @memoize(key='called')
        ... def say(something, also='lmao'):
        ...     print(something, also)
        >>> say('ayy')
        ayy lmao
        >>> say(something='ayy')
        ayy lmao
        >>> say('ayy', 'lmao')
        ayy lmao
        >>> say('ayy', also='lmao')
        ayy lmao
        >>> say('ayy')
        >>> say(something='ayy')
        >>> say('ayy', 'lmao')
        >>> say('ayy', also='lmao')

    Keyword argument ordering is still ignored, though:

        >>> say(something='ayy', also='lmao')
        ayy lmao
        >>> say(also='lmao', something='ayy')

    If key is 'positional', the cache key uses only the positional
    arguments. This may provide slightly better performance, but
    disallows passing keyword args, and may interact unexpectedly with
    default values:

        >>> @memoize(key='positional')
        ... def say(something, also='lmao'):
        ...     print(something, also)
        >>> say('ayy')
        ayy lmao
        >>> say('ayy', 'lmao')
        ayy lmao
        >>> say('ayy')
        >>> say('ayy', 'lmao')
        >>> say('ayy', also='lmao')
        Traceback (most recent call last):
          ...
        TypeError: memoized() got an unexpected keyword argument 'also'

    In any case, argument values must be hashable:

        >>> say(['ayy', 'lmao'])
        Traceback (most recent call last):
          ...
        TypeError: unhashable type: 'list'

    Also, some functions may not have an inspectable signature, and will
    raise ValueError if memoized with the default key:

        >>> print_once = memoize(print, key='positional')
        >>> print_once = memoize(print, key='called')
        >>> print_once = memoize(print)
        Traceback (most recent call last):
          ...
        ValueError: no signature found for builtin <built-in function print>

    A custom cache or key function may be provided to work around either
    of these issues.

    The default cache is a regular, non-evicting dict: unless explicitly
    removed, memoized results will remain in the cache, preventing them
    from being garbage collected, until the cache itself is deleted --
    frequently until the program exits. See functools.lru_cache for an
    alternative memoizer with a limited-size cache.
    """
    # This construct allows the user to either call this decorator with
    # optional keyword args, or just apply it directly to a function.
    if func is ...:
        # The decorator was called with optional keyword args:
        # return another decorator which uses them when applied.
        return partial(memoize, cache=cache, key=key)
    # The decorator was applied to a function.

    if cache is ...:
        cache = {}

    if key == 'positional':
        # Define this version separately to avoid extraneous calls to a
        # pass-through key function. (The cost adds up in inner loops!)
        @wraps(func)
        def memoized(*args):
            try:
                return cache[args]
            except KeyError:
                cache[args] = result = func(*args)
            return result
    else:
        if key == 'received':
            key = freeze_as_received(func)
        elif key == 'called':
            key = freeze
        # Otherwise, assume key is a custom function

        @wraps(func)
        def memoized(*args, **kwargs):
            cache_key = key(*args, **kwargs)
            try:
                return cache[cache_key]
            except KeyError:
                cache[cache_key] = result = func(*args, **kwargs)
            return result

    memoized._cache = cache
    memoized._key = key

    return memoized


def cache(func=..., *, key='received'):
    """Memoize the function using weak references.

    Once the decorated function has been called with a given signature,
    it will return the same object for all subsequent calls with that
    signature, as long as another non-weak reference to the object still
    exists.

        >>> class WeakReferenceableList(list):
        ...     pass  # Built-in lists can't be weak-referenced

        >>> @cache
        ... def say(word, also='lmao'):
        ...     return WeakReferenceableList([word, also])
        >>> say('ayy') is say('ayy')
        True
        >>> say('ayy') is say('ayy', 'lmao')
        True
        >>> say('ayy') is say('ayy', also='lmao')
        True
        >>> say('ayy') is say(also='lmao', word='ayy')
        True
    """
    return memoize(func, cache=weakref.WeakValueDictionary(), key=key)


def freeze_as_received(func):
    """Compute "frozen" signatures, applying default values."""
    sig = signature(func)

    def freeze(*args, **kwargs):
        ba = sig.bind(*args, **kwargs)
        ba.apply_defaults()
        return ba.args, frozenset(ba.kwargs.items())

    return freeze


def freeze(*args, **kwargs):
    return args, frozenset(kwargs.items())


def only_args(*args, **kwargs):
    return args


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


def instance_cached(cls=..., *, cache=cache):
    """Decorator to cache a class' instances.

        >>> @instance_cached
        ... class Test:
        ...     def __new__(cls, value=1):
        ...         print('__new__', value)
        ...         return object.__new__(cls)
        ...     def __init__(self, value=1):
        ...         print('__init__', value)
        ...         self.value = value

    tl;dr: constructors with the same arguments return the same object:

        >>> Test(1) is Test(1)
        __new__ 1
        __init__ 1
        True

    The default cache function only holds each value as long as another
    non-weak reference to it remains.

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

    Default argument values are handled appropriately:

        >>> default = Test()
        >>> default is t
        True
        >>> Test() is Test(1) is Test(value=1)
        True

    Cached instances are deleted when no more references remain, and
    subsequent constructor calls execute normally:

        >>> del t
        >>> Test(1) is Test(1)
        True
        >>> del default
        >>> t = Test()
        __new__ 1
        __init__ 1
        >>> t = Test()

        >>> t.value, Test().value, Test(1).value, Test(value=1).value
        (1, 1, 1, 1)

    Names, docstrings, etc. are unaffected:

        >>> Test.__new__.__qualname__
        'Test.__new__'
        >>> Test.__init__.__qualname__
        'Test.__init__'

    Can be used with other caches, which may behave differently:

        >>> from functools import lru_cache
        >>> @instance_cached(cache=lru_cache(maxsize=1))
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
        TypeError: object.__new__() takes exactly one argument (the type to instantiate)

        >>> @instance_cached
        ... class Test:
        ...     def __new__(cls, meh):
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
        TypeError: missing a required argument: 'meh'

        >>> @instance_cached
        ... class Test:
        ...     def __init__(self, meh):
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
        TypeError: __init__() missing 1 required positional argument: 'meh'

    """  # noqa: E501 line too long
    # This construct allows the user to either call this decorator with
    # optional keyword args, or just apply it directly to a function.
    if cls is ...:
        # The decorator was called with optional keyword args:
        # return another decorator which uses them when applied.
        return partial(instance_cached, cache=cache)
    # The decorator was applied to a function.

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

    @cache
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


def lru_cache(maxsize=128):
    """Basic-but-decent implementation, for use in Python 2.

    Doesn't work with keyword args, and doesn't provide cache_info()
    like Python 3's functools.lru_cache(). Also doesn't support the
    'typed' argument, so cache keys consider only objects' __eq__(), not
    their types.

    *Does* set cache_clear() on the decorated function.

    This might not be the most performant implementation out there, but
    it's short, easy to understand, and copy-pasteable.
    """

    def decorator(func, maxsize=maxsize):
        cache = OrderedDict()
        # Store local references to these functions
        # to avoid extra dict lookups in the wrapper
        # (same reason as maxsize=maxsize above)
        cache_pop = cache.pop
        cache_popitem = cache.popitem
        cache_setitem = cache.__setitem__
        cache_len = cache.__len__

        @wraps(func)
        def wrapper(*args):
            try:
                result = cache_pop(args)
            except KeyError:
                result = func(*args)
            # Move the result to the last, "most recently used" position
            cache_setitem(args, result)

            # int is implemented in C, so using a local reference to
            # maxsize.__lt__ doesn't help performance.
            # OrderedDict is implemented in C in Python 3, but not in
            # Python 2, so cache.__len__ does help.
            if cache_len() > maxsize:
                # Remove the first, "least recently used" item
                cache_popitem(last=False)

            return result

        wrapper.cache_clear = cache.clear
        return wrapper
    return decorator
