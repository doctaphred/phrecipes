from itertools import product


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
