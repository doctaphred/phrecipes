from functools import partial, partialmethod
from operator import attrgetter, itemgetter, methodcaller


class each:
    """Generator expressions? Too verbose.

    >>> each('123', int)
    each([1, 2, 3])
    >>> each(range(5)).real
    each([0, 1, 2, 3, 4])
    >>> sum(each(range(5)).imag)
    0
    >>> ''.join(each('abc').upper())
    'ABC'
    >>> each('123').to(int)
    each([1, 2, 3])
    >>> each(['123', '456'])[1].to(int)
    each([2, 5])
    >>> each('abc') == 'a'
    each([True, False, False])
    >>> each(range(5)) < 3
    each([True, True, True, False, False])
    >>> 3 > each(range(5))
    each([True, True, True, False, False])
    >>> each(range(5)) >= 3
    each([False, False, False, True, True])
    >>> abs(each(range(-3, 3)))
    each([3, 2, 1, 0, 1, 2])

    >>> each([range(1), range(2)]).contains(0, 1)
    each([False, True])
    >>> each(range(5)).is_in(range(1, 3))
    each([False, True, True, False, False])

    >>> e = each([{'a': 1}, {'a': 2}])
    >>> e
    each([{'a': 1}, {'a': 2}])
    >>> e.values().contains(1)
    each([True, False])
    >>> e['a']
    each([1, 2])
    >>> e['b'] = 2
    >>> del e['a']
    >>> e
    each([{'b': 2}, {'b': 2}])

    >>> e['b'] += 1
    Traceback (most recent call last):
      ...
    NotImplementedError: <class 'itercools.each'> does not support __iadd__
    """

    def __init__(self, iterable, effect=None):
        self.__effect = effect
        self.__it = iterable

    def to(self, func, *args, **kwargs):
        return self.__class__(self, partial(func, *args, **kwargs))

    def contains(self, *values, fold=all):
        def effect(self):
            return fold(value in self for value in values)
        return self.to(effect)

    def is_in(self, *containers, fold=all):
        def effect(self):
            return fold(self in container for container in containers)
        return self.to(effect)

    def __getattr__(self, name):
        """Call this method directly to access overloaded names.

        >>> each('spam').to
        <bound method each.to of each(['s', 'p', 'a', 'm'])>
        >>> each('spam').__getattr__('to')
        Traceback (most recent call last):
          ...
        AttributeError: 'str' object has no attribute 'to'
        """
        return self.to(attrgetter(name))

    def __setattr__(self, name, value):
        if name.startswith('_'):
            # TODO: move to __init__?
            return super().__setattr__(name, value)
        for element in self:
            setattr(self, name, value)

    def __delattr__(self, name):
        if name.startswith('_'):
            # TODO: remove?
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
        return 'each([{}])'.format(', '.join(self.to(repr)))

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
