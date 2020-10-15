"""Create type-safe dynamic namedtuples by abusing ordered kwargs!

Example usage:

    >>> r1 = record(ayy='lmao', foo='bar')
    >>> r2 = record(ayy='lmao', foo='bar')

    >>> r1
    record(ayy='lmao', foo='bar')
    >>> r2
    record(ayy='lmao', foo='bar')

    >>> r1 == r2
    True

Records with the same fields, in the same order, have the same type:

    >>> type(r1) is type(r2)
    True

Records are hashable:

    >>> r1 in {r1}
    True

    >>> r1 in {r2}
    True

Records with different values are not equal, but still have the same type:

    >>> r3 = record(ayy='lmao', foo='baz')

    >>> r1 == r3 or r2 == r3
    False
    >>> r3 in (r1, r2)
    False
    >>> type(r1) is type(r3)
    True

Different field orders result in different, inequivalent types:

    >>> r4 = record(foo='baz', ayy='lmao')

    >>> r3.ayy == r4.ayy and r3.foo == r4.foo
    True

    >>> r3 == r4
    False

    >>> type(r4) is type(r3)
    False

Instances are cached:

    >>> r1 is r2
    True

Caching is implemented via weakrefs, so instances are destroyed when no
non-weak references remain:

    >>> id1 = id(record(a=1, b=2))
    >>> id2 = id(record(a=1, b=2))
    >>> id1 == id2
    False

    >>> ref = record(a=1, b=2)
    >>> id1 = id(record(a=1, b=2))
    >>> id2 = id(record(a=1, b=2))
    >>> id1 == id2
    True
    >>> del ref
    >>> id1 = id(record(a=1, b=2))
    >>> id2 = id(record(a=1, b=2))
    >>> id1 == id2
    False

Note, however, that implicit references may persist during the
evaluation of certain expressions:

    >>> record(a=1, b=2) is record(a=1, b=2)
    True

Derivative records can be created by calling instances:

    >>> r5 = r1(foo='baz')
    >>> r5
    record(ayy='lmao', foo='baz')

Caching still applies to new records created this way:

    >>> r5 is r3
    True

Records have no __dict__, but can easily create one:

    >>> vars(r1)
    Traceback (most recent call last):
      ...
    TypeError: vars() argument must have __dict__ attribute

    >>> dict(r1)
    {'ayy': 'lmao', 'foo': 'bar'}
"""
from weakref import WeakValueDictionary


class VintageRecordStore(dict):
    """Simpler implementation of records using namedtuples.

    Tuple subclasses, including namedtuples, don't support weakrefs; so
    records created this way cannot be instance-cached.

    See https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots
    """

    def __call__(self, **attrs):
        return self[tuple(attrs)](**attrs)

    def __missing__(self, key):
        from collections import namedtuple
        self[key] = cls = namedtuple('record', key)
        return cls


class RecordMeta(type):
    """Metaclass which dynamically creates subclasses and caches instances."""
    _subclasses = WeakValueDictionary()
    _instances = WeakValueDictionary()

    def __call__(cls, **kwargs):
        key = tuple(kwargs.items())
        try:
            instance = cls._instances[key]
        except KeyError:
            instance = cls._instances[key] = cls.create_instance(kwargs)
        return instance

    def get_subclass(cls, fields):
        try:
            subclass = cls._subclasses[fields]
        except KeyError:
            subclass = cls._subclasses[fields] = cls.create_subclass(fields)
        return subclass

    def create_instance(cls, kwargs):
        subclass = cls.get_subclass(tuple(kwargs))
        subclass_super = super(type(subclass), subclass)
        return subclass_super.__call__(**kwargs)

    def create_subclass(cls, fields):
        return type(f"{cls.__name__}_sub", (cls,), {'__slots__': fields})


class record(metaclass=RecordMeta):
    """Auto-cached, slots-based data class.

    Similar to namedtuple, but with less nonsense and weakref support.
    """
    __slots__ = ['__weakref__']

    def __init__(self, **attrs):
        for name, value in attrs.items():
            setattr(self, name, value)

    def __call__(self, **updates):
        """Construct a new record based on this instance, with some updates."""
        return type(self)(**{**dict(self), **updates})  # 😚👌

    def __iter__(self):
        """Iterate over key-value PAIRS, as G-d intended."""
        for name in dir(self):
            if not name.startswith('_'):
                yield name, getattr(self, name)

    def __repr__(self):
        return 'record({})'.format(
            ', '.join(f'{name}={value!r}' for name, value in self)
        )

    # Instances are cached, so equivalence is just identity!
