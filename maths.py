from itertools import count, product


def is_prime(n):
    """Quick n dirty primality test.

    >>> assert not is_prime(0)
    >>> assert not is_prime(1)
    >>> assert is_prime(2)
    >>> assert is_prime(3)
    >>> assert not is_prime(4)

    >>> primes = primes()
    >>> for n in range(1, 10_000):
    ...     if is_prime(n):
    ...         p = next(primes)
    ...         if n != p:
    ...             print(n, p)

    """
    assert isinstance(n, int) and n >= 0, n
    if n < 2:
        return False
    max_divisor = int(n ** 0.5)
    return all(n % d for d in range(2, max_divisor + 1))


def primes():
    """Yield prime numbers, starting with 2.

    Algorithm adapted from David Eppstein, Alex Martelli, Tim Hochberg,
    and Eratosthenes of Cyrene.

    See http://code.activestate.com/recipes/117119/#c2
    and https://en.wikipedia.org/wiki/Sieve_of_Eratosthenes

    >>> p = primes()
    >>> [next(p) for _ in range(18)]
    [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47, 53, 59, 61]
    """
    yield 2  # Special-case the only even prime, then skip even numbers.
    witnessed = {}  # Map composites to their "witnesses".
    for n in count(3, step=2):  # Skip even numbers.
        try:
            # We won't see n again, so its witness is no longer needed.
            witness = witnessed.pop(n)
        except KeyError:  # No witness: n is prime.
            yield n
            # Since n is prime, it is the only divisor of n**2. Record
            # 2n as the witness because we're skipping even numbers.
            witnessed[n ** 2] = n * 2
        else:
            # Move the witness to its next multiple, skipping any which
            # already have another witness.
            n += witness
            while n in witnessed:
                n += witness
            witnessed[n] = witness


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
