from functools import partial, wraps
import weakref


def freeze(*args, **kwargs):
    return args, frozenset(kwargs.items())


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
        if key not in cache:
            result = func(*args, **kwargs)
            cache[key] = result
        else:
            result = cache[key]
        return result

    wrapper._cache = cache
    wrapper._cache_key = key_func
    return wrapper


class WeakCached(type):
    __call__ = weak_cached(type.__call__)
