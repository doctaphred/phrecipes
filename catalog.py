class Catalog:

    def __init__(self, initial=None):
        self._maps = initial

    @classmethod
    def of(cls, *maps):
        return cls({id(m): m for m in maps})

    def add(self, m=None):
        if m is None:
            m = {}
        index = id(m)
        self._maps[index] = m
        return index

    def get(self, index):
        return self._maps[index]

    def pop(self, index):
        return self._maps.pop(index)

    def __getitem__(self, key):
        return dict(self._get_all(key))

    def _get_all(self, key):
        for index, m in self._maps.items():
            try:
                yield index, m[key]
            except KeyError:
                pass

    def __setitem__(self, key, value):
        for m in self._maps.values():
            m[key] = value

    def __delitem__(self, key):
        for m in self._maps.values():
            try:
                del m[key]
            except KeyError:
                pass

    def __contains__(self, key):
        return self.contains(key)

    def contains(self, key, fold=any):
        return fold(key in m for m in self._maps.values())

    def containing(self, key):
        return self.__class__(
            {i: m for i, m in self._maps.items() if key in m})

    def not_containing(self, key):
        return self.__class__(
            {i: m for i, m in self._maps.items() if key not in m})

    def matching(self, *predicates, fold=any):
        return self.__class__(
            {i: m for i, m in self._maps.items() if predicate(m)})

    def not_matching(self, *predicates, fold=all):
        return self.__class__(
            {i: m for i, m in self._maps.items() if not predicate(m)})
