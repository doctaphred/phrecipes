"""
See https://docs.python.org/3/library/itertools.html#itertools-recipes
for more cool recipes!
"""
from collections import defaultdict
from itertools import tee, filterfalse
from functools import wraps


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
        if result not in results:
            results[result] = set()
        results[result].add(item)
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


def remember(iterable, history=None):
    """Record an iterable's output in a list as it is traversed.

    >>> it, history = remember(range(5))
    >>> next(it)
    0
    >>> next(it)
    1
    >>> history
    [0, 1]
    >>> list(it)
    [2, 3, 4]
    >>> history
    [0, 1, 2, 3, 4]
    """
    if history is None:
        history = []

    def recorder():
        for x in iter(iterable):
            history.append(x)
            yield x

    return recorder(), history


def reuse(gen_func):
    """Reuse a generator!"""
    history = []
    gen = gen_func()

    @wraps(gen_func)
    def reusable():
        yield from history
        for element in gen:
            history.append(element)
            yield element

    return reusable


class each:
    """Generator expressions? Too verbose.

    >>> list(each(range(5)).real)
    [0, 1, 2, 3, 4]
    >>> sum(each(range(5)).imag)
    0
    >>> ''.join(each('abc').upper())
    'ABC'
    >>> list(each('123').to(int))
    [1, 2, 3]
    """

    def __init__(self, iterable, effect=None):
        self.__effect = effect
        self.__it = iterable

    def to(self, func):
        return each(self, func)

    def __getattr__(self, name):
        def effect(self):
            return getattr(self, name)
        return each(self, effect)

    def __call__(self, *args, **kwargs):
        def effect(self):
            return self(*args, **kwargs)
        return each(self, effect)

    def __iter__(self):
        if self.__effect is None:
            yield from self.__it
        else:
            for thing in self.__it:
                yield self.__effect(thing)


if __name__ == '__main__':
    import doctest
    doctest.testmod()
