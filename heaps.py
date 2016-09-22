import heapq


class Heap:
    """Simple wrapper around heapq functions.

    Why the standard library doesn't a class like this is beyond me...
    """

    def __init__(self, items=None):
        if items is None:
            self._items = []
        else:
            heapq.heapify(items)
            self._items = items

    def push(self, item):
        return heapq.heappush(self._items, item)

    def pop(self):
        return heapq.heappop(self._items)

    def pushpop(self, item):
        return heapq.pushpop(self._items)

    def replace(self, item):
        return heapq.heapreplace(self._items, item)

    def peek(self):
        return self._items[0]
