from collections import defaultdict, deque
from functools import partial

from coolections import DynamicDefaultDict
from funccools import call_until


def _furcate(key, *, predicate, queues, iterator):
    dequeue_all = partial(call_until, IndexError, queues[key].popleft)

    def enqueue(element, *, predicate=predicate, queues=queues):
        queues[predicate(element)].append(element)

    yield from dequeue_all()
    for element in iterator:
        enqueue(element)
        yield from dequeue_all()


def furcate(predicate, iterable):
    """Split an iterable on a predicate.

    The predicate can return any hashable value.

    Returns a defaultdict mapping each predicate result to an iterator
    of matching items from the iterable.

        >>> groups = furcate(str.lower, 'aYy LmAo')
        >>> ''.join(groups['a'])
        'aA'
        >>> ''.join(groups['y'])
        'Yy'
        >>> ''.join(groups['l'])
        'L'
        >>> ''.join(groups['x'])
        ''
        >>> ''.join(groups['o'])
        'o'
    """
    return DynamicDefaultDict(partial(
        _furcate,
        predicate=predicate,
        queues=defaultdict(deque),
        iterator=iter(iterable),
    ))


def nfurcate(predicate, iterable, *, n):
    """Split an iterable into n groups on a predicate which returns an index.

    Returns a tuple of iterators. The items yielded from the iterator at
    each index are the elements of ``iterable`` for which the predicate
    returns that index.

        >>> other, lower = nfurcate(str.islower, 'aYy LmAo', n=2)
        >>> ''.join(other)
        'Y LA'
        >>> ''.join(lower)
        'aymo'

        >>> groups = nfurcate(len, ['ayy', 'lmao'], n=5)
        >>> list(groups[3])
        ['ayy']
        >>> list(groups[4])
        ['lmao']

    All returned iterators are one-time-use only.

        >>> [list(group) for group in groups]
        [[], [], [], [], []]
    """
    get_queue = partial(
        _furcate,
        predicate=predicate,
        queues=[deque() for _ in range(n)],
        iterator=iter(iterable),
    )
    return tuple(get_queue(i) for i in range(n))


bifurcate = partial(nfurcate, n=2)
