import heapq
from functools import partial


class Heap:
    """Simple wrapper around heapq functions.

        >>> h = Heap()
        >>> h.push((5, 'write code'))
        >>> h.push((7, 'release product'))
        >>> h.push((1, 'write spec'))
        >>> h.push((3, 'create tests'))
        >>> h.pop()
        (1, 'write spec')

    Look Ma, heapsort!

        >>> list(Heap([1, 3, 5, 7, 9, 2, 4, 6, 8, 0]))
        [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]

    """

    def __init__(self, items=None):
        if items is None:
            self._items = []
        else:
            self._items = list(items)
            heapq.heapify(self._items)
        for name in ['push', 'pop', 'pushpop', 'replace']:
            func = getattr(heapq, 'heap' + name)
            setattr(self, name, partial(func, self._items))

    def peek(self):
        return self._items[0]

    def __bool__(self):
        return bool(self._items)

    def __len__(self):
        return len(self._items)

    def __contains__(self, obj):
        """Prevent implicit destructive iteration.

        >>> h = Heap()
        >>> 'ayy' in h
        False
        >>> h.push('ayy')
        >>> 'ayy' in h
        True
        >>> 'ayy' in h
        True
        >>> h.pop()
        'ayy'
        >>> 'ayy' in h
        False
        """
        return any(item == obj for item in self._items)

    def __next__(self):
        try:
            return self.pop()
        except IndexError:
            raise StopIteration

    def __iter__(self):
        return self


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

    def __init__(self):
        from itertools import count
        self._heap = []
        self._counter = count()

    def _wrap(self, item, priority):
        # Entries are stored as tuples, which heapq compares when they
        # are pushed or popped. The priority and a unique ID are stored
        # as the first two elements to make sure the item itself is
        # never included in any comparison.
        #
        # The heapq module implements a min-heap, so invert the priority
        # and make the IDs monotonically increase to ensure stability.
        return (-priority, next(self._counter), item)

    def push(self, item, priority=0):
        heapq.heappush(self._heap, self._wrap(item, priority))

    def pop(self):
        return heapq.heappop(self._heap)[-1]

    def pushpop(self, item, priority=0):
        return heapq.heappushpop(self._heap, self._wrap(item, priority))[-1]

    def replace(self, item, priority=0):
        return heapq.heapreplace(self._heap, self._wrap(item, priority))[-1]

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
        return self._heap[0][-1]

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

    def __contains__(self, item):
        """Prevent implicit destructive iteration.

        >>> q = PriorityQueue()
        >>> 'ayy' in q
        False
        >>> q.push('ayy')
        >>> 'ayy' in q
        True
        >>> 'ayy' in q
        True
        >>> q.pop()
        'ayy'
        >>> 'ayy' in q
        False
        """
        return any(entry[-1] == item for entry in self._heap)

    def __next__(self):
        try:
            return self.pop()
        except IndexError:
            raise StopIteration

    def __iter__(self):
        return self
