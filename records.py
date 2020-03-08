"""Create type-safe dynamic namedtuples by abusing ordered kwargs!

>>> r1 = record(ayy='lmao', foo='bar')
>>> r2 = record(ayy='lmao', foo='bar')
>>> r3 = record(foo='bar', ayy='lmao')
>>> r1 == r2
True
>>> type(r1) is type(r2)
True
>>> r2 == r3
False
>>> type(r2) is type(r3)
False
"""


class RecordStore(dict):

    def __call__(self, **fields):
        return self[tuple(fields)](**fields)

    def __missing__(self, key):
        from collections import namedtuple
        self[key] = result = namedtuple('record', key)
        return result


record = RecordStore()
