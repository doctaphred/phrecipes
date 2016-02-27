"""
See https://docs.python.org/3/library/itertools.html#itertools-recipes
for more cool recipes!

See also the toolz project for more cool functional programming helpers:
https://github.com/pytoolz/toolz
"""
from collections import defaultdict
from collections.abc import Iterator
from functools import lru_cache, partial, wraps
from itertools import tee, filterfalse


def filters(iterable, *predicates):
    """Filter the iterable on each given predicate.

    >>> div_by_two = lambda x: not x % 2
    >>> div_by_three = lambda x: not x % 3
    >>> twos, threes = filters(range(10), div_by_two, div_by_three)
    >>> list(twos)
    [0, 2, 4, 6, 8]
    >>> list(threes)
    [0, 3, 6, 9]
    """
    tees = tee(iterable, len(predicates))
    return tuple(filter(pred, t) for pred, t in zip(predicates, tees))


def partition(iterable, predicate):
    """Divide the iterable into two iterables according to the predicate.

    >>> evens, odds = partition(range(10), lambda x: not x % 2)
    >>> list(evens)
    [0, 2, 4, 6, 8]
    >>> list(odds)
    [1, 3, 5, 7, 9]
    """
    t1, t2 = tee(iterable)
    return filter(predicate, t1), filterfalse(predicate, t2)


def matches(iterable, predicate, value):
    """Yield elements of iterable for which predicate(element) == value.

    >>> list(matches(range(10), lambda x: x % 3, 2))
    [2, 5, 8]
    """
    for element in iterable:
        if predicate(element) == value:
            yield element


def lazydivvy(iterable, predicate, values):
    """Map values to iterables of elements whose predicate returns that value.

    See divvy for an eager version that doesn't require specifying values.

    >>> remainders = lazydivvy(range(10), lambda x: x % 3, range(3))
    >>> for remainder, values in sorted(remainders.items()):
    ...    print(remainder, list(values))
    0 [0, 3, 6, 9]
    1 [1, 4, 7]
    2 [2, 5, 8]
    """
    tees = tee(iterable, len(values))
    return {value: matches(t, predicate, value)
            for t, value in zip(tees, values)}


def divvy(iterable, predicate):
    """Divvy up an iterable into a dict of sets.

    >>> remainders = divvy(range(10), lambda x: x % 3)
    >>> for remainder, divisors in sorted(remainders.items()):
    ...     print(remainder, sorted(divisors))
    0 [0, 3, 6, 9]
    1 [1, 4, 7]
    2 [2, 5, 8]
    """
    results = {}
    for item in iterable:
        result = predicate(item)
        try:
            bag = results[result]
        except KeyError:
            results[result] = bag = set()
        bag.add(item)
    return results


def defaultdivvy(iterable, predicate):
    """Divvy up an iterable into a defaultdict of sets.

    >>> remainders = defaultdivvy(range(10), lambda x: x % 3)
    >>> for remainder, divisors in sorted(remainders.items()):
    ...     print(remainder, sorted(divisors))
    0 [0, 3, 6, 9]
    1 [1, 4, 7]
    2 [2, 5, 8]
    """
    results = defaultdict(set)
    for item in iterable:
        results[predicate(item)].add(item)
    return results


def unique(iterable, key=None):
    """Yield unique elements, preserving order."""
    if key is None:
        return _unique(iterable)
    return _unique_key(iterable, key)


def _unique(iterable):
    """
    >>> ''.join(_unique('AAAABBBCCDAABBB'))
    'ABCD'
    """
    seen = set()
    see = seen.add  # Avoid inner-loop name lookup
    for element in filterfalse(seen.__contains__, iterable):
        see(element)
        yield element


def _unique_key(iterable, key):
    """
    >>> ''.join(_unique_key('ABBCcAD', key=str.casefold))
    'ABCD'
    """
    seen = set()
    see = seen.add  # Avoid inner-loop name lookup
    for element in iterable:
        k = key(element)
        if k not in seen:
            see(k)
            yield element


def reuse(func=None, *, cache=lru_cache()):
    """Cache and reuse a generator function across multiple calls."""
    # Allow this decorator to work with or without being called
    if func is None:
        return partial(reuse, cache=cache)

    # Either initialize an empty history and start a new generator, or
    # retrieve an existing history and the already-started generator
    # that produced it
    @cache
    def resume(*args, **kwargs):
        return [], func(*args, **kwargs)

    @wraps(func)
    def reuser(*args, **kwargs):
        history, gen = resume(*args, **kwargs)
        yield from history
        record = history.append  # Avoid inner-loop name lookup
        for x in gen:
            record(x)
            yield x

    return reuser


class Peekable(Iterator):
    """
    >>> p = Peekable(range(3))
    >>> next(p)
    0
    >>> next(p)
    1
    >>> p.peek()
    2
    >>> p.peek(default=None)
    2
    >>> bool(p)
    True
    >>> next(p)
    2
    >>> bool(p)
    False
    >>> p.peek()
    Traceback (most recent call last):
      ...
    StopIteration
    >>> p.peek(default=None)
    >>> next(p)
    Traceback (most recent call last):
      ...
    StopIteration
    >>> list(Peekable(range(3)))
    [0, 1, 2]
    """

    def __init__(self, it):
        self.__it = iter(it)
        self.__advance()

    def __advance(self):
        try:
            self.__next_val = next(self.__it)
        except StopIteration:
            self.__empty = True
        else:
            self.__empty = False

    def peek(self, **kwargs):
        """Return the next item without advancing the iterator.

        Raises StopIteration if the iterator is empty, unless a default
        value is provided as a kwarg.
        """
        if self.__empty:
            try:
                return kwargs['default']
            except KeyError:
                raise StopIteration
        return self.__next_val

    def __next__(self):
        if self.__empty:
            raise StopIteration
        val = self.__next_val
        self.__advance()
        return val

    def __bool__(self):
        return not self.__empty


if __name__ == '__main__':
    import doctest
    doctest.testmod()
