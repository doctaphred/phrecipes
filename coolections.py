from collections.abc import Mapping
from itertools import chain

from itercools import unique


def all_eq(objs):
    """Check if all elements of objs compare equal.

    objs must support .count() and .__getitem__() (like list or tuple),
    and each obj's .__eq__() must behave semi-reasonably.
    """
    assert objs
    matches = objs.count(objs[0])
    assert matches  # objs[0] == objs[0] must return True
    return matches == len(objs)


class MISSING:
    """Sentinel denoting "key not in mapping".

    Implemented as a class instead of object() for serializability.
    """
    pass


def values(mappings, key, missing=MISSING):
    for mapping in mappings:
        try:
            # Only __getitem__() is required; don't use get()
            yield mapping[key]
        except KeyError:
            yield missing


def diffs(*mappings, missing=MISSING):
    """Yield keys and values which differ between the two mappings.

    A 'mapping' is any object which implements keys() and __getitem__().
    """
    assert mappings
    assert all(isinstance(mapping, Mapping) for mapping in mappings)

    # Defer to __eq__(), even if it contradicts the algorithm below
    if all_eq(mappings):
        return

    keys = chain.from_iterable(mapping.keys() for mapping in mappings)
    for key in unique(keys):
        vals = tuple(values(mappings, key))
        if not all_eq(vals):
            yield key, vals


def value_not_none(k, v):
    return v is not None


def subdict(d, keys=None, item_filter=value_not_none):
    """Construct a "subset" of a dictionary.

    First filters keys based on the `keys` whitelist, then filters items
    based on the `item_filter` function. If either filter is None, it
    will not be applied.

    With no arguments, simply filters out None values:

        >>> subdict({'a': 1})
        {'a': 1}
        >>> subdict({'a': 1, 'b': None})
        {'a': 1}

    With `keys`, filters out non-matching keys:

        >>> subdict({'a': 1, 'b': 2}, ['a'])
        {'a': 1}

        >>> subdict({'a': 1, 'b': 2, 'c': None}, ['a', 'c'])
        {'a': 1}

    The default `item_filter` may be altered or removed:

        >>> def val_gt_1(key, value):
        ...     return value > 1

        >>> subdict({'a': 1, 'b': 2}, item_filter=val_gt_1)
        {'b': 2}

        >>> subdict({'a': None}, item_filter=None)
        {'a': None}

    Both `keys` and `item_filter` may be provided:

        >>> subdict({'a': 1, 'b': 2, 'c': 3}, ['a', 'b'], item_filter=val_gt_1)
        {'b': 2}

    Args:
        d: a dictionary
        keys: a subset of the dictionary's keys, or None to use all keys
        item_filter: function(key, value) -> bool, or None to use all items
    """
    if keys is None:
        filtered_keys = d
    else:
        filtered_keys = d.keys() & keys  # Python 2: set(d).intersection(keys)

    if item_filter is None:
        return {k: d[k] for k in filtered_keys}
    else:
        subdict = {}
        for k in filtered_keys:
            v = d[k]
            if item_filter(k, v):
                subdict[k] = v
        return subdict


class CascadingDict:
    """Please never actually use this.

    Update: use ChainMap instead:
    https://docs.python.org/3.5/library/collections.html#collections.ChainMap

    >>> d1 = CascadingDict(a=1)
    >>> d2 = d1.extended(a=2)
    >>> d3 = d1.extended(a=3)
    >>> d4 = d2.extended(b=4)

    >>> d1['a']
    1
    >>> d1['b']
    Traceback (most recent call last):
      ...
    KeyError: 'b'

    >>> d2
    CascadingDict(a=2)
    >>> d2['a'] = 5
    >>> d2
    CascadingDict(a=5)

    >>> d1
    CascadingDict(a=1)
    >>> d3
    CascadingDict(a=3)
    >>> d4
    CascadingDict(b=4, [a=5])
    >>> d5 = d4.extended(c=7)
    >>> d5
    CascadingDict(c=7, [b=4, a=5])
    >>> list(d5.items())
    [('c', 7), ('b', 4), ('a', 5)]
    >>> d5.extended(b=2)
    CascadingDict(b=2, [c=7, a=5])
    >>> del d4['a']
    Traceback (most recent call last):
      ...
    KeyError: 'a'
    >>> del d4['b']
    >>> d4
    CascadingDict([a=5])
    >>> d5
    CascadingDict(c=7, [a=5])

    >>> d2
    CascadingDict(a=5)
    >>> del d2['a']
    >>> d2
    CascadingDict([a=1])
    >>> d4
    CascadingDict([a=1])

    >>> {**d4}
    {'a': 1}

    Actually, maybe it's not so bad:

    >>> default = CascadingDict(
    ...     notify='alert@saas.com',
    ...     customer='customer@localhost')
    >>> dev = default.extended(notify='alert@localhost')
    >>> prod = default.extended(customer='customer@customer.com')
    >>> prod
    CascadingDict(customer='customer@customer.com', [notify='alert@saas.com'])
    >>> dev
    CascadingDict(notify='alert@localhost', [customer='customer@localhost'])
    """

    parent = None

    def __init__(self, **items):
        self.contents = items

    def extended(self, **items):
        new = self.__class__(**items)
        new.parent = self
        return new

    def __getitem__(self, name):
        obj = self
        while obj is not None:
            contents = obj.contents
            if name in contents:
                return contents[name]
            obj = obj.parent
        raise KeyError(name)

    def __setitem__(self, name, value):
        self.contents[name] = value

    def __delitem__(self, name):
        del self.contents[name]

    def keys(self):
        for key, value in self.items():
            yield key

    def values(self):
        for key, value in self.items():
            yield value

    def items(self):
        yield from self.contents.items()
        yield from self.inherited_items()

    def inherited_items(self):
        seen = set(self.contents.keys())
        see = seen.add  # Avoid inner-loop name lookup
        obj = self

        while obj is not None:
            for key, value in obj.contents.items():
                if key not in seen:
                    yield key, value
                    see(key)
            obj = obj.parent

    def __iter__(self):
        yield from self.keys()

    def __repr__(self):
        own = ', '.join(
            '{}={!r}'.format(key, value)
            for key, value in self.contents.items())

        inherited = ', '.join(
            '{}={!r}'.format(key, value)
            for key, value in self.inherited_items())

        if own and inherited:
            return 'CascadingDict({}, [{}])'.format(own, inherited)
        elif own:
            return 'CascadingDict({})'.format(own)
        elif inherited:
            return 'CascadingDict([{}])'.format(inherited)
        else:
            return 'CascadingDict()'
