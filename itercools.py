"""
See https://docs.python.org/3/library/itertools.html#itertools-recipes
for more cool recipes!

See also the toolz project for more cool functional programming helpers:
https://github.com/pytoolz/toolz
"""
import operator as op
from collections import defaultdict, deque
from collections.abc import Iterator
from functools import lru_cache, partial, wraps
from itertools import chain, filterfalse, islice, tee


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


def unique(*iterables, key=None):
    """Yield unique elements, preserving order.

    >>> ''.join(unique('AAAABBBCCDAABBB'))
    'ABCD'
    >>> ''.join(unique('AAAA', 'BBBC', 'CDA', 'ABBB'))
    'ABCD'
    >>> ''.join(unique('ABBCcAD', key=str.casefold))
    'ABCD'
    """
    combined = chain.from_iterable(iterables)
    yielded = set()
    # Avoid inner-loop name lookups
    already_yielded = yielded.__contains__
    remember = yielded.add

    if key is None:
        for element in filterfalse(already_yielded, combined):
            remember(element)
            yield element

    else:
        for element in combined:
            k = key(element)
            if not already_yielded(k):
                remember(k)
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


def last(iterator):
    """Consume an iterator and return the last element.

    >>> it = iter(range(10))
    >>> last(it)
    9

    >>> last(it)
    Traceback (most recent call last):
      ...
    StopIteration
    """
    q = deque(iterator, maxlen=1)
    try:
        return q[0]
    except IndexError:
        raise StopIteration


def tail(n, iterator):
    """Consume an iterator and return the last n element(s) as a deque.

    >>> it = iter(range(10))
    >>> tail(2, it)
    deque([8, 9], maxlen=2)
    >>> tail(1, it)
    deque([], maxlen=1)
    """
    return deque(iterator, maxlen=n)


def advance(n, iterator):
    """Consume and discard the next n element(s) of the iterator.

    >>> it = (print(i) for i in range(3))
    >>> advance(2, it)
    0
    1
    >>> advance(1, it)
    2
    >>> advance(1, it)
    Traceback (most recent call last):
      ...
    StopIteration
    """
    if not deque(islice(iterator, n), maxlen=1):
        raise StopIteration


def exhaust(iterator):
    """Call next on an iterator until it stops.

    >>> it = (print(i) for i in range(2))
    >>> exhaust(it)
    0
    1
    >>> exhaust(it)
    """
    deque(iterator, maxlen=0)


def genlen(iterator):
    """Exhaust the iterator and return the number of values yielded.

    >>> it = iter(range(10))
    >>> genlen(it)
    10
    >>> genlen(it)
    0
    """
    return sum(1 for _ in iterator)


def intersperse(sep, it):
    """Like str.join for iterators.

    Raises StopIteration if the iterator is initially empty.
    """
    it = iter(it)
    yield next(it)
    for elem in it:
        yield sep
        yield elem


def check(func, seq, *, allow_empty=False):
    """Wrap a sequence, raising ValueError if the function fails."""
    for i, item in enumerate(seq):
        if not func(item):
            raise ValueError(f"{item!r} at position {i}")
        yield item


def check_cmp(cmp, seq, *, allow_empty=False):
    """Wrap a sequence, raising ValueError if the comparison fails.

    >>> list(check_cmp(op.lt, [1, 2]))
    [1, 2]
    >>> list(check_cmp(op.le, [1, 1]))
    [1, 1]
    >>> list(check_cmp(op.lt, [1, 1]))
    Traceback (most recent call last):
      ...
    ValueError: 1 followed by 1 at position 1

    >>> list(check_cmp(op.lt, []))
    Traceback (most recent call last):
      ...
    ValueError: empty sequence
    >>> list(check_cmp(op.lt, [], allow_empty=True))
    []
    """
    it = iter(seq)
    try:
        prev = next(it)
    except StopIteration:
        if allow_empty:
            return
        else:
            raise ValueError("empty sequence")

    yield prev

    for i, item in enumerate(it, start=1):
        if not cmp(prev, item):
            raise ValueError(
                f"{prev!r} followed by {item!r} at position {i}"
            )
        prev = item
        yield item


ensure_monotonic_increasing = partial(check_cmp, op.le)
ensure_strict_monotonic_increasing = partial(check_cmp, op.lt)
ensure_monotonic_decreasing = partial(check_cmp, op.ge)
ensure_strict_monotonic_decreasing = partial(check_cmp, op.gt)


def check_monotonic_increasing(*args, **kwargs):
    return exhaust(check_cmp(*args, **kwargs))


if __name__ == '__main__':
    import doctest
    doctest.testmod()
