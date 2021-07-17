Extended doctests for ``stats``
===============================

..
    >>> from stats import *


Stats are computed quickly, even over 1 million samples:

    >>> from time import perf_counter as clock
    >>> start = clock()
    >>> s = Stats(range(1_000_000))
    >>> s.pprint()
    Stats(
        count=1000000,
        first=0,
        last=999999,
        min=0,
        max=999999,
        sum=499999500000,
        mean=499999.5,
        ssdm=8.333333333324998e+16,
        # variance: 83333416666.66666
        # stdev: 288675.27893234405
    )
    >>> end = clock()
    >>> assert end - start < 0.5


Addition works as expected:

    >>> s = Stats([0])
    >>> s
    Stats(count=1, first=0, last=0, min=0, max=0, sum=0, mean=0, ssdm=0)

    >>> s + [1]
    Stats(count=2, first=0, last=1, min=0, max=1, sum=1, mean=0.5, ssdm=0.5)

    >>> s += [1]
    >>> s
    Stats(count=2, first=0, last=1, min=0, max=1, sum=1, mean=0.5, ssdm=0.5)


Works with sum():

    >>> sum([[2], [3]], s)
    Stats(count=4, first=0, last=3, min=0, max=3, sum=6, mean=1.5, ssdm=5.0)


In-place addition reassigns, and doesn't mutate:

    >>> s0 = s1 = Stats([0])
    >>> assert s1 is s0
    >>> assert s1 == s0
    >>> s1 += [0]
    >>> assert s1 is not s0  # s1 has been reassigned.
    >>> assert s1 != s0  # Its value has changed.


Empty samples don't change any values:

    >>> s0 = s1 = Stats([0])
    >>> assert s1 is s0
    >>> assert s1 == s0
    >>> s1 += ()
    >>> assert s1 is not s0  # s1 has been reassigned.
    >>> assert s1 == s0  # Its value has *not* changed.
    >>> assert repr(s1) == repr(s0)  # mean and ssdm are still ints.


Miscellaneous corner cases:

    >>> Stats([0]).pprint()
    Stats(
        count=1,
        first=0,
        last=0,
        min=0,
        max=0,
        sum=0,
        mean=0,
        ssdm=0,
        # variance: 0.0
        # stdev: 0.0
    )

    >>> Stats([1]).pprint()
    Stats(
        count=1,
        first=1,
        last=1,
        min=1,
        max=1,
        sum=1,
        mean=1,
        ssdm=0,
        # variance: 0.0
        # stdev: 0.0
    )

    >>> Stats([])
    Traceback (most recent call last):
      ...
    StopIteration
