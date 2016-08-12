"""
>>> odict['a': 1, 'b': 2, 'c': 3]
OrderedDict([('a', 1), ('b', 2), ('c', 3)])

>>> odict['a': 1]
OrderedDict([('a', 1)])

>>> odict('a', 1, 'b', 2, 'c', 3)
OrderedDict([('a', 1), ('b', 2), ('c', 3)])

>>> odict('a', 1)
OrderedDict([('a', 1)])

>>> odict()
OrderedDict()
"""
from collections import OrderedDict

from magic import magic


@magic
class odict:
    """OrderedDict builder with nice syntax."""
    def __getitem__(self, key):
        try:
            # Assume key is a tuple of slices
            items = [(s.start, s.stop) for s in key]
        except TypeError:
            # Assume key is a single slice
            items = [(key.start, key.stop)]
        return OrderedDict(items)

    def __call__(self, *kv):
        items = zip(kv[::2], kv[1::2]) if kv else []
        return OrderedDict(items)
