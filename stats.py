import warnings


def mean(sum, count):
    """x̄"""
    return sum / count


def variance(ssdm, count):
    """Unbiased sample variance, using Bessel's correction (s²)."""
    try:
        return ssdm / (count - 1)
    except ZeroDivisionError:
        return 0


def stdev(ssdm, count):
    """s"""
    return variance(ssdm, count) ** 0.5


x̄, s, s2 = mean, stdev, variance


def indented(obj, template='    {}'):
    return template.format(obj)


def indented_lines(*lines, template='    {}', sep='\n'):
    return sep.join(indented(line, template) for line in lines)


class Stats:
    """Calculate running statistics of a sequence of samples.

    Uses Welford's method for computing variance.

    See https://www.johndcook.com/blog/standard_deviation/

    >>> Stats(range(100_000))
    Stats:
        100,000 samples, Σ=4,999,950,000
        first=0, last=99,999
        min=0, max=99,999
        x̄=5e+04, s=2.89e+04

    >>> s = Stats([0]); s
    Stats:
        1 sample, Σ=0
        first=0, last=0
        min=0, max=0
        x̄=0, s=0
    >>> s.add(-2.0); s
    Stats:
        2 samples, Σ=-2.0
        first=0, last=-2.0
        min=-2.0, max=0
        x̄=-1, s=1.41

    >>> Stats([])
    Traceback (most recent call last):
      ...
    StopIteration
    """
    things = (
        'first',
        'last',
        'min',
        'max',
        'sum',
        'mean',
    )
    __slots__ = things + (
        'count',
        'ssdm',  # Sum of squared deviations from the mean.
    )

    def __init__(self, samples):
        it = iter(samples)
        sample = next(it)
        for attr in self.things:
            setattr(self, attr, sample)
        self.count = 1
        self.ssdm = 0
        self.update(it)

    def add(self, sample):
        """Update stats with a new sample."""
        self.last = sample
        self.count += 1
        self.sum += sample
        if sample < self.min:
            self.min = sample
        elif sample > self.max:
            self.max = sample

        diff = sample - self.mean
        self.mean += diff / self.count
        # Compute additional squared deviation using
        # both the previous and current means.
        self.ssdm += diff * (sample - self.mean)

    def update(self, samples):
        """Update stats with multiple samples."""
        sample = self.last
        smallest = self.min
        largest = self.max
        total = self.sum
        mean = self.mean
        count = self.count
        ssdm = self.ssdm

        for sample in samples:
            count += 1
            total += sample
            if sample < smallest:
                smallest = sample
            elif sample > largest:
                largest = sample

            diff = sample - mean
            mean += diff / count
            # Compute additional squared deviation using
            # both the previous and current means.
            ssdm += diff * (sample - mean)

        self.last = sample
        self.min = smallest
        self.max = largest
        self.sum = total
        self.mean = mean
        self.count = count
        self.ssdm = ssdm

        if __debug__:
            if self.precision_loss > 1e-6:
                warnings.warn(f"Precision loss of {self.precision_loss}")

    @property
    def variance(self):
        return variance(self.ssdm, self.count)

    @property
    def stdev(self):
        return stdev(self.ssdm, self.count)

    @property
    def precision_loss(self):
        return abs(self.sum / self.count - self.mean)

    def _update_slow(self, samples):
        """Same as above, but about half as fast for a list of 1M ints.

        Sure looks a lot prettier, though.
        """
        for sample in samples:
            self.count += 1
            self.sum += sample
            self.min = min(self.min, sample)
            self.max = max(self.max, sample)

            diff = sample - self.mean
            self.mean += diff / self.count
            # Compute additional squared deviation using
            # both the previous and current means.
            self.ssdm += diff * (sample - self.mean)

        self.last = sample

        assert self.sum / self.count - self.mean < 1e-6

    def __repr__(self):
        s = 's' if self.count > 1 else ''
        return "{}:\n{}".format(
            type(self).__name__,
            indented_lines(
                f"{self.count:,} sample{s}, Σ={self.sum:,}",
                f"first={self.first:,}, last={self.last:,}",
                f"min={self.min:,}, max={self.max:,}",
                f"x̄={self.mean:,.3g}, s={self.stdev:,.3g}",
            ),
        )

    # TODO: __format__
    # >>> import datetime
    # >>> d = datetime.datetime(2010, 7, 4, 12, 15, 58)
    # >>> '{:%Y-%m-%d %H:%M:%S}'.format(d)
    # '2010-07-04 12:15:58'

    # TODO: __add__, __or__, __iadd__, etc

    @property
    def x̄(self):
        return self.mean

    @property
    def s(self):
        return self.stdev

    @property
    def s2(self):
        return self.variance

    @property
    def Σs2(self):
        return self.ssdm


def stats(samples):
    """Compute statistics in a single pass over the samples.

    Returns a tuple: (first, last, min, max, sum, mean, count, Σσ²)

    Uses Welford's method for computing variance.

    See https://www.johndcook.com/blog/standard_deviation/
    """
    it = iter(samples)
    first = sample = smallest = largest = total = mean = next(it)
    count = 1
    ssdm = 0  # Sum of squared deviations from the mean.

    for sample in it:
        count += 1
        total += sample
        if sample < smallest:
            smallest = sample
        elif sample > largest:
            largest = sample

        diff = sample - mean
        mean += diff / count
        # Compute additional squared deviation using
        # both the previous and current means.
        ssdm += diff * (sample - mean)

    return first, sample, smallest, largest, total, mean, ssdm
