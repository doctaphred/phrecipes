"""Create type-safe dynamic namedtuples by abusing ordered kwargs!

Example usage:

    >>> r_orig = record(foo='ayy', bar='lmao')
    >>> r_same = record(foo='ayy', bar='lmao')

    >>> r_orig
    record(foo='ayy', bar='lmao')
    >>> r_same
    record(foo='ayy', bar='lmao')

    >>> r_orig == r_same
    True

Records with the same fields, in the same order, have the same type:

    >>> type(r_orig) is type(r_same)
    True

Records are hashable:

    >>> r_orig in {r_orig}
    True

    >>> r_orig in {r_same}
    True

Records with different values are not equal, but still have the same type:

    >>> r_diff = record(foo='ayy', bar='wat')

    >>> r_orig == r_diff or r_same == r_diff
    False
    >>> r_diff in (r_orig, r_same)
    False
    >>> type(r_orig) is type(r_diff)
    True

Different field orders result in different, inequivalent types:

    >>> r_forward = record(foo='ayy', bar='lmao')
    >>> r_reverse = record(bar='lmao', foo='ayy')

    >>> r_forward.foo == r_reverse.foo and r_forward.bar == r_reverse.bar
    True

    >>> r_forward == r_reverse
    False

    >>> type(r_reverse) is type(r_forward)
    False

Instances are cached:

    >>> r_orig is r_same
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

    >>> r_derived = r_orig(bar='wat')
    >>> r_derived
    record(foo='ayy', bar='wat')

Caching still applies to new records created this way:

    >>> r_derived is r_diff
    True

Records have no __dict__, but can easily create one:

    >>> vars(r_orig)
    Traceback (most recent call last):
      ...
    TypeError: vars() argument must have __dict__ attribute

    >>> dict(r_orig)
    {'foo': 'ayy', 'bar': 'lmao'}
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
        for name in self.__class__.__slots__:
            if not name.startswith('_'):
                yield name, getattr(self, name)

    def __repr__(self):
        return 'record({})'.format(
            ', '.join(f'{name}={value!r}' for name, value in self)
        )

    # Instances are cached, so equivalence is just identity!
