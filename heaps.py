import heapq


class Heap:
    """Simple wrapper around heapq functions.

    Why the standard library doesn't include a class like this is beyond me...
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


class PriorityQueue:
    """Priority queue implemented using a heap.

    This implementation ensures stability: items with the same priority
    are returned in the order they were added, and the values of the
    items themselves are never compared.

        >>> q = PriorityQueue()
        >>> q.push('lmao')
        >>> q.push('ayy', priority=1)
        >>> while q:
        ...     print(q.pop())
        ayy
        lmao

    The queue may be destructively iterated over:

        >>> q.push('ayy')
        >>> q.push('lmao')
        >>> len(q), list(q)
        (2, ['ayy', 'lmao'])
        >>> len(q), list(q)
        (0, [])

    """

    def __init__(self, items=None):
        from itertools import count
        self._heap = []
        self._counter = count()

    def push(self, item, priority=0):
        from heapq import heappush
        # Entries are stored as tuples, which heapq compares when they
        # are pushed or popped. The priority and a unique ID are stored
        # as the first two elements to make sure the item itself is
        # never included in any comparison.
        #
        # The heapq module implements a min-heap, so invert the priority
        # and make the IDs monotonically increase to ensure stability.
        heappush(self._heap, (-priority, next(self._counter), item))

    def pop(self):
        from heapq import heappop
        _, _, item = heappop(self._heap)
        return item

    def peek(self):
        """
        >>> q = PriorityQueue()
        >>> q.peek()
        Traceback (most recent call last):
          ...
        IndexError: list index out of range
        >>> q.push(None)
        >>> q.peek()
        """
        _, _, item = self._heap[0]
        return item

    def __bool__(self):
        """
        >>> q = PriorityQueue()
        >>> bool(q)
        False
        >>> q.push(None)
        >>> bool(q)
        True
        >>> q.pop()
        >>> bool(q)
        False
        """
        return bool(self._heap)

    def __len__(self):
        """
        >>> q = PriorityQueue()
        >>> len(q)
        0
        >>> q.push(None)
        >>> len(q)
        1
        >>> q.pop()
        >>> len(q)
        0
        """
        return len(self._heap)

    def __next__(self):
        try:
            return self.pop()
        except IndexError:
            raise StopIteration

    def __iter__(self):
        return self
