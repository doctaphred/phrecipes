Extended doctests for ``stats``
===============================

..
    >>> from stats import *


Stats are computed quickly, even over 1 million samples:

    >>> from time import perf_counter as clock
    >>> start = clock()
    >>> pstats(range(1_000_000))
    count: 1000000
    first: 0
    last: 999999
    smallest: 0
    largest: 999999
    total: 499999500000
    mean: 499999.5
    variance: 83333416666.66666
    >>> end = clock()
    >>> assert end - start < 0.5


Miscellaneous corner cases:

    >>> stats([0]).values()
    dict_values([1, 0, 0, 0, 0, 0, 0, 0.0])

    >>> stats([1]).values()
    dict_values([1, 1, 1, 1, 1, 1, 1, 0.0])

    >>> stats([])
    Traceback (most recent call last):
      ...
    StopIteration
