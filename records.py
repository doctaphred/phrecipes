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

TODO: instances *could* be cached, but are currently not:

    >>> r1 is r2
    False

(tuple subclasses don't support weakrefs, so this might be tricky:
https://docs.python.org/3/reference/datamodel.html#notes-on-using-slots)
"""


class RecordStore(dict):

    def __call__(self, **fields):
        return self[tuple(fields)](**fields)

    def __missing__(self, key):
        from collections import namedtuple
        self[key] = result = namedtuple('record', key)
        return result


record = RecordStore()
