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
