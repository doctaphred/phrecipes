from collections import namedtuple
from math import isclose
import warnings


class stats(namedtuple('stats', [
    'count',
    'first',
    'last',
    'min',
    'max',
    'sum',
    'mean',
    'ssdm',  # Sum of squared deviations from the mean.
])):
    """Calculate running statistics in a single pass over a sequence.

    Uses Welford's method with Bessel's correction for computing the
    unbiased sample variance.

    See https://www.johndcook.com/blog/standard_deviation/
    and https://en.wikipedia.org/wiki/Bessel%27s_correction

    Example:

        >>> stats([1, 2, 3]).pprint()
        stats(
            count=3,
            first=1,
            last=3,
            min=1,
            max=3,
            sum=6,
            mean=2.0,
            ssdm=2.0,
            # variance: 1.0
            # stdev: 1.0
        )

    (Note that the unbiased sample variance is 1.0, not 2/3.)

    stats can be updated with any iterable:

        >>> stats([1]) + [2] + iter([3])
        stats(count=3, first=1, last=3, min=1, max=3, sum=6, mean=2.0, ssdm=2.0)

    stats instances are immutable; in-place addition is reassignment:

        >>> s1 = s2 = stats(b'ayy')
        >>> s2 += b'lmao'
        >>> assert s1 != s2

    stats instances can be combined (including their variance!):

        >>> combined = stats([1]) | stats([2]) | stats([3])
        >>> assert combined == stats([1, 2, 3])
    """

    def __new__(cls, *args, **kwargs):
        if not kwargs and len(args) == 1:
            return cls.of(*args)
        else:
            return super().__new__(cls, *args, **kwargs)

    @classmethod
    def of(cls, samples):
        samples = iter(samples)
        first = last = min = max = sum = mean = next(samples)
        self = cls(1, first, last, min, max, sum, mean, 0)
        return self + samples

    @classmethod
    def wrap(cls, samples):
        """
        >>> for x in stats.wrap([1, 2, 3]):
        ...     print(x.last, x)
        1 stats(count=1, first=1, last=1, min=1, max=1, sum=1, mean=1, ssdm=0)
        2 stats(count=2, first=1, last=2, min=1, max=2, sum=3, mean=1.5, ssdm=0.5)
        3 stats(count=3, first=1, last=3, min=1, max=3, sum=6, mean=2.0, ssdm=2.0)
        """
        samples = iter(samples)
        first = last = min = max = sum = mean = next(samples)
        self = cls(1, first, last, min, max, sum, mean, 0)
        yield self
        for sample in samples:
            self += [sample]
            yield self

    def __add__(self, samples):
        """Update the stats with additional samples."""
        assert not isinstance(samples, stats), "merge stats with |, not +"
        count, first, last, min, max, sum, mean, ssdm = self

        for last in samples:
            count += 1
            sum += last
            if last < min:
                min = last
            elif last > max:
                max = last

            prev_dev = last - mean
            mean += prev_dev / count
            # Welford's method: compute additional squared deviation using
            # the deviation from both the previous and current means.
            ssdm += prev_dev * (last - mean)

        return self.__class__(count, first, last, min, max, sum, mean, ssdm)

    def merge(*stats):
        """Merge the data from multiple stats instances."""
        assert stats
        count = sum(s.count for s in stats)
        total = sum(s.sum for s in stats)
        combined_mean = total / count
        combined_ssdm = sum(s._ssdm(combined_mean) for s in stats)

        first, *_, last = stats

        return first.__class__(
            count=count,
            # Assume the stats objects were provided in order.
            first=first.first,
            last=last.last,
            min=min(s.min for s in stats),
            max=max(s.max for s in stats),
            sum=total,
            mean=combined_mean,
            ssdm=combined_ssdm,
        )

    def _ssdm(self, combined_mean):
        """Partial sum of squared deviations from the combined mean."""
        return self.ssdm + self.count * (self.mean - combined_mean) ** 2

    __or__ = merge

    def __eq__(self, other):
        """Check for equality within the bounds of floating point precision."""
        if not isinstance(other, stats):
            return NotImplemented
        return all(isclose(s, o) for s, o in zip(self, other))

    @property
    def variance(self):
        """Unbiased sample variance, using Bessel's correction.

        See https://en.wikipedia.org/wiki/Bessel%27s_correction
        """
        try:
            # Bessel's correction: use n - 1 to reduce sample bias.
            return self.ssdm / (self.count - 1)
        except ZeroDivisionError:
            return 0.0

    @property
    def stdev(self):
        """Standard deviation (using the unbiased sample variance)."""
        return self.variance ** 0.5

    @property
    def precision_loss(self):
        return abs(self.sum / self.count - self.mean)

    if __debug__:  # Only check precision in non-optimized mode.
        def __init__(self, *args, **kwargs):
            if self.precision_loss > 1e-6:
                warnings.warn(f"precision loss of {self.precision_loss:.1e}")

    @property
    def pretty(self):
        return '\n'.join(self._pretty())

    def _pretty(self):
        yield f"{self.__class__.__name__}("
        for name, value in zip(self._fields, self):
            yield f"    {name}={value},"
        yield f"    # variance: {self.variance}"
        yield f"    # stdev: {self.stdev}"
        yield ")"

    def pprint(self):
        print(self.pretty)
