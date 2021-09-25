from itertools import count, product


def primes():
    """Yield prime numbers, starting with 2.

    Algorithm by David Eppstein, Alex Martelli, and Tim Hochberg:
    http://code.activestate.com/recipes/117119/#c2

    >>> p = primes()
    >>> [next(p) for _ in range(10)]
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
    """
    yield 2
    # Map composites to primes witnessing their compositeness
    composites = {}
    # Skip even numbers
    for n in count(3, step=2):
        # We won't see n again, so we can delete its witness, if any
        prime_divisor = composites.pop(n, None)
        if prime_divisor is None:
            # n is prime
            yield n
            # Record n as a divisor of its square
            composites[n ** 2] = 2 * n
        else:
            # n is composite
            # Move the witness to a new multiple
            x = n + prime_divisor
            while x in composites:
                x += prime_divisor
            composites[x] = prime_divisor


def reordered_digit_map(exponents, base=2):
    """Construct a mapping which answers the question:

    If a base's exponents are applied to a number's digits in arbitrary
    order (rather than the conventional greatest-to-least/"big-endian"
    ordering), what will its conventionally-calculated value be?

    Since every possible value will be included in this mapping, it is
    implemented as an indexable tuple rather than a dict.

    >>> reordered_digit_map([1, 0])
    (0, 1, 2, 3)
    >>> reordered_digit_map([0, 1])
    (0, 2, 1, 3)
    """
    assert sorted(exponents) == list(range(len(exponents)))
    digit_values = range(base)
    return tuple(
        sum(digit * (base ** exponent)
            for digit, exponent in zip(digits, exponents))
        for digits in product(digit_values, repeat=len(exponents))
    )
