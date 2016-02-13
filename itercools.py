"""
See https://docs.python.org/3/library/itertools.html#itertools-recipes
for more cool recipes!
"""
from collections import defaultdict
from functools import _make_key, partialmethod, wraps
from itertools import tee, filterfalse
from operator import attrgetter, itemgetter, methodcaller


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


def record(iterable, history=None):
    """Record an iterable's output in a list as it is traversed.

    >>> it, history = record(range(5))
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
        for element in iter(iterable):
            history.append(element)
            yield element

    return recorder(), history


def remember(gen_func):
    """Remember and reuse a generator's output."""
    memory = {}

    @wraps(gen_func)
    def rememberer(*args, **kwargs):
        key = _make_key(args, kwargs, True)
        try:
            seen, unseen = memory[key]
        except KeyError:
            memory[key] = seen, unseen = [], gen_func(*args, **kwargs)
        see = seen.append  # Avoid inner-loop name lookup

        yield from seen
        for element in unseen:
            see(element)
            yield element

    return rememberer


class each:
    """Generator expressions? Too verbose.

    >>> each('123', int)
    <1, 2, 3>
    >>> each(range(5)).real
    <0, 1, 2, 3, 4>
    >>> sum(each(range(5)).imag)
    0
    >>> ''.join(each('abc').upper())
    'ABC'
    >>> each('123').to(int)
    <1, 2, 3>
    >>> each(['123', '456'])[1].to(int)
    <2, 5>
    >>> each('abc') == 'a'
    <True, False, False>
    >>> each(range(5)) < 3
    <True, True, True, False, False>
    >>> 3 > each(range(5))
    <True, True, True, False, False>
    >>> each(range(5)) >= 3
    <False, False, False, True, True>
    >>> abs(each(range(-3, 3)))
    <3, 2, 1, 0, 1, 2>

    >>> each([range(1), range(2)]).contains(0, 1)
    <False, True>
    >>> each(range(5)).is_in(range(1, 3))
    <False, True, True, False, False>

    >>> e = each([{'a': 1}, {'a': 2}])
    >>> e
    <{'a': 1}, {'a': 2}>
    >>> e.values().contains(1)
    <True, False>
    >>> e['a']
    <1, 2>
    >>> e['b'] = 2
    >>> del e['a']
    >>> e
    <{'b': 2}, {'b': 2}>

    >>> e['b'] += 1
    Traceback (most recent call last):
      ...
    NotImplementedError: <class 'itercools.each'> does not support __iadd__
    """

    def __init__(self, iterable, effect=None):
        self.__effect = effect
        self.__it = iterable

    def to(self, func):
        return self.__class__(self, func)

    def contains(self, *values, fold=all):
        def effect(self):
            return fold(value in self for value in values)
        return self.to(effect)

    def is_in(self, *containers, fold=all):
        def effect(self):
            return fold(self in container for container in containers)
        return self.to(effect)

    def __getattr__(self, name):
        return self.to(attrgetter(name))

    def __setattr__(self, name, value):
        if name.startswith('_'):
            return super().__setattr__(name, value)
        for element in self:
            setattr(self, name, value)

    def __delattr__(self, name):
        if name.startswith('_'):
            return super().__delattr__(name)
        for element in self:
            delattr(self, name)

    def __getitem__(self, key):
        return self.to(itemgetter(key))

    def __setitem__(self, name, value):
        for element in self:
            element[name] = value

    def __delitem__(self, name):
        for element in self:
            del element[name]

    def __iter__(self):
        if self.__effect is None:
            yield from self.__it
        else:
            for thing in self.__it:
                yield self.__effect(thing)

    def _apply(self, name, *args, **kwargs):
        # TODO: Joe says use operator.X instead of methodcaller
        return self.to(methodcaller(name, *args, **kwargs))

    def __repr__(self):
        return '<{}>'.format(', '.join(self.to(repr)))

    _broadcast_methods = [
        '__lt__',
        '__le__',
        '__eq__',
        '__ne__',
        '__ge__',
        '__gt__',
        '__abs__',
        '__add__',
        '__and__',
        '__call__',
        # '__concat__',  # Not actually a real special method
        # '__contains__',  # `in` casts the return value to bool
        '__divmod__',
        '__floordiv__',
        # '__index__',  # Must return an int
        '__inv__',
        '__invert__',
        # '__len__',  # Must return an int
        '__lshift__',
        '__mod__',
        '__mul__',
        '__matmul__',
        '__neg__',
        '__or__',
        '__pos__',
        '__pow__',
        '__rshift__',
        '__sub__',
        '__truediv__',
        '__xor__',

        # TODO: ?
        # '__missing__',
        # '__reversed__',

        # TODO: do I dare?
        # '__enter__',
        # '__exit__',

        # TODO: metaclass with these:
        # '__instancecheck__',
        # '__subclasscheck__',
        ]

    for name in _broadcast_methods:
        locals()[name] = partialmethod(_apply, name)
    del name

    def _nope(self, name, *args, **kwargs):
        raise NotImplementedError(
            '{0.__class__} does not support {1}'.format(self, name))

    # TODO: make these work
    _unsupported_methods = [
        '__iadd__',
        '__iand__',
        '__iconcat__',
        '__ifloordiv__',
        '__ilshift__',
        '__imod__',
        '__imul__',
        '__imatmul__',
        '__ior__',
        '__ipow__',
        '__irshift__',
        '__isub__',
        '__itruediv__',
        '__ixor__',
        ]
    for name in _unsupported_methods:
        locals()[name] = partialmethod(_nope, name)
    del name


if __name__ == '__main__':
    import doctest
    doctest.testmod()
