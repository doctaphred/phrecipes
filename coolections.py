from collections.abc import Mapping, MutableMapping
from itertools import chain
from pathlib import Path
from weakref import finalize, WeakValueDictionary

from itercools import unique


class DynamicDefaultDict(dict):
    """Like a defaultdict, but passes the missing key to its factory function.

    >>> ddd = DynamicDefaultDict([0].__mul__)
    >>> ddd
    DynamicDefaultDict(__mul__, {})

    >>> ddd[0]
    []
    >>> ddd
    DynamicDefaultDict(__mul__, {0: []})

    >>> ddd[1][0] += 1
    >>> ddd
    DynamicDefaultDict(__mul__, {0: [], 1: [1]})

    >>> @DynamicDefaultDict
    ... def fibs(n):
    ...     return fibs(n - 1) + fibs(n - 2)
    >>> fibs[0], fibs[1] = 1, 1
    >>> fibs(10)
    89
    >>> fibs.values()
    dict_values([1, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89])
    """

    def __init__(self, factory, *args, **kwargs):
        self.factory = factory
        super().__init__(*args, **kwargs)

    def __missing__(self, key):
        self[key] = result = self.factory(key)
        return result

    def __repr__(self):
        s = super().__repr__()
        return f"{self.__class__.__name__}({self.factory.__name__}, {s})"

    # Use it as a decorator!
    __call__ = dict.__getitem__


class IdentityDict(MutableMapping):
    """A dict keyed off of object IDs -- hashability not required.

    >>> L = []
    >>> d = IdentityDict([(L, 'lmao')])

    >>> d[L]
    'lmao'
    >>> L in d
    True
    >>> [] in d
    False
    >>> d[[]]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    KeyError: 'id ... of object []'

    >>> L.append('ayy')
    >>> d[L]
    'lmao'
    >>> d[['ayy']]  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    KeyError: "id ... of object ['ayy']"

    >>> list(d.items())
    [(['ayy'], 'lmao')]

    >>> d  # doctest: +ELLIPSIS
    IdentityDict:
        ... (['ayy']): 'lmao'
    """
    _init_keys = dict
    _init_values = dict

    def __init__(*others, **kwargs):
        self, *others = others  # Allow self to be a kwarg.
        self._keys = self._init_keys()
        self._values = self._init_values()
        for other in others:
            self.update(other)
        self.update(kwargs)

    def update(self, other):
        if isinstance(other, Mapping):
            for k in other:
                self[k] = other[k]
        else:
            for k, v in other:
                self[k] = v

    def __getitem__(self, obj):
        try:
            return self._values[id(obj)]
        except KeyError as exc:
            raise KeyError(f"id {id(obj)} of object {obj}") from exc

    def __setitem__(self, obj, value):
        self._keys[id(obj)] = obj
        self._values[id(obj)] = value

    def __delitem__(self, obj):
        del self._keys[id(obj)]
        del self._values[id(obj)]

    def __iter__(self):
        return iter(self._keys.values())

    def __len__(self):
        return len(self._values)

    def __repr__(self):
        contents = ''.join(
            f"\n    {id(key)} ({key!r}): {self[key]!r}"
            for key in self
        )
        if not contents:
            contents = " <empty>"
        return f"{self.__class__.__name__}:{contents}"


class WeakKeyIdentityDictionary(IdentityDict):
    _init_keys = WeakValueDictionary

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        finalize(key, lambda: self._values.pop(id(key), None))


class WeakValueIdentityDictionary(IdentityDict):
    _init_values = WeakValueDictionary

    def __setitem__(self, key, value):
        super().__setitem__(key, value)
        finalize(value, lambda: self._keys.pop(id(key), None))


class DirDict(MutableMapping):
    """A dict backed by a directory of files."""
    # TODO: Handle additional error conditions.

    def __init__(self, path):
        self._dir = Path(path).resolve()

    def __getitem__(self, key):
        try:
            return self.path(key).read_text()
        except FileNotFoundError:
            return self.__missing__(key)

    def __missing__(self, key):
        raise KeyError(key)

    def __setitem__(self, key, value):
        self._dir.mkdir(parents=True, exist_ok=True)
        self.path(key).write_text(value)

    def __delitem__(self, key):
        try:
            self.path(key).unlink()
        except FileNotFoundError as exc:
            raise KeyError(key) from exc

    def __contains__(self, key):
        return self.path(key).exists()

    def __iter__(self):
        return self._dir.iterdir()

    def __len__(self):
        return sum(1 for _ in self)

    def path(self, key=None):
        if key is None:
            return self._dir
        path = (self._dir / key).resolve()
        assert self._dir in path.parents
        return path

    def __repr__(self):
        return f"{self.__class__.__name__}({self._dir!r})"


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
