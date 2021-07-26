"""Create type-safe dynamic namedtuples by abusing ordered kwargs!

Example usage:

    >>> r_orig = record(foo='ayy', bar='lmao')
    >>> r_same = record(foo='ayy', bar='lmao')

    >>> r_orig
    record(foo='ayy', bar='lmao')
    >>> r_same
    record(foo='ayy', bar='lmao')

    >>> assert r_orig == r_same

Records with the same fields, in the same order, have the same type:

    >>> assert type(r_orig) is type(r_same)

Records are hashable:

    >>> assert r_orig in {r_orig}
    >>> assert r_orig in {r_same}

Records with different values are not equal, but still have the same type:

    >>> r_diff = record(foo='ayy', bar='wat')

    >>> assert r_orig != r_diff and r_same != r_diff
    >>> assert r_diff not in (r_orig, r_same)
    >>> assert type(r_orig) is type(r_diff)

Different field orders result in different, inequivalent types:

    >>> r_forward = record(foo='ayy', bar='lmao')
    >>> r_reverse = record(bar='lmao', foo='ayy')

    >>> assert r_forward.foo == r_reverse.foo and r_forward.bar == r_reverse.bar
    >>> assert r_forward != r_reverse
    >>> assert type(r_reverse) is not type(r_forward)

Their type names indicate this difference:

    >>> print(type(r_forward))
    <class 'records.record['foo', 'bar']'>

    >>> print(type(r_reverse))
    <class 'records.record['bar', 'foo']'>

Instances are cached:

    >>> assert r_orig is r_same

Caching is implemented via weakrefs, so instances are destroyed when no
non-weak references remain:

    >>> id1 = id(record(a=1, b=2))
    >>> id2 = id(record(a=1, b=2))
    >>> assert id1 != id2

    >>> ref = record(a=1, b=2)
    >>> id1 = id(record(a=1, b=2))
    >>> id2 = id(record(a=1, b=2))
    >>> assert id1 == id2

    >>> del ref
    >>> id1 = id(record(a=1, b=2))
    >>> id2 = id(record(a=1, b=2))
    >>> assert id1 != id2

Note, however, that implicit references may persist during the
evaluation of certain expressions:

    >>> assert record(a=1, b=2) is record(a=1, b=2)

Derivative records can be created by calling instances:

    >>> r_derived = r_orig(bar='wat')
    >>> r_derived
    record(foo='ayy', bar='wat')

Derivative records subclass the base record class, not each other:

    >>> for cls in record(a=1)(b=2)(c=3).__class__.__mro__: print(cls)
    <class 'records.record['a', 'b', 'c']'>
    <class 'records.record'>
    <class 'object'>

Caching still applies to new records created this way:

    >>> assert r_orig() is r_orig
    >>> assert r_orig(foo='ayy') is r_orig
    >>> assert r_orig(foo='ayy', bar='lmao') is r_orig
    >>> assert r_orig(bar='lmao') is r_orig

Even when the fields are provided in a different order in the call:

    >>> assert r_orig(bar='lmao', foo='ayy') is r_orig

    (TODO: This does not seem ideal, but I'm not sure what to do instead.)

New fields can also be added this way:

    >>> r_orig(baz='new')
    record(foo='ayy', bar='lmao', baz='new')

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
        """Return a record instance with the given fields."""
        key = tuple(kwargs.items())
        try:
            instance = cls._instances[key]
        except KeyError:
            instance = cls._instances[key] = cls.create_instance(kwargs)
        return instance

    def __getitem__(cls, fields):
        """Return a record subclass with the given fields."""
        if not isinstance(fields, tuple):
            fields = (fields,)
        try:
            subclass = cls._subclasses[fields]
        except KeyError:
            subclass = cls._subclasses[fields] = cls.create_subclass(fields)
        return subclass

    def create_instance(cls, kwargs):
        subclass = cls[tuple(kwargs)]
        subclass_super = super(type(subclass), subclass)
        return subclass_super.__call__(**kwargs)

    def create_subclass(cls, fields):
        if fields:
            fields_repr = ', '.join(map(repr, fields))
            name = f"{cls.__name__}[{fields_repr}]"
        else:
            name = cls.__name__
        return type(name, (cls,), {'__slots__': fields})


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
        return record(**{**dict(self), **updates})  # 😚👌

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
