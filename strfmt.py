import sys


class SafeSub(dict):
    """Use with str.format_map to leave missing keys untouched.

    >>> '{key} {missing key}'.format_map(SafeSub({'key': 'value'}))
    'value {missing key}'
    """
    def __missing__(self, key):
        return '{' + key + '}'


class KeyReplacer(dict):
    """Use with str.format_map to strip curly braces from missing keys.

    '{key} {missing key}'.format_map(KeyReplacer({'key': 'value'}))
    'value missing key'
    """
    def __missing__(self, key):
        return key


def fmt(s, **kwargs):
    """Format the string using local variables.

    Additional variables may be specified via kwargs, which override
    any local variable names.

    Missing names do not raise exceptions.

    >>> x = 2; fmt('{x} {y}')
    '2 {y}'
    """
    # Frame hack: get locals() from one level up
    keys = SafeSub(sys._getframe(1).f_locals)
    keys.update(kwargs)
    return s.format_map(keys)


def pl(singular, plural, zero=None, placeholder='#'):
    """Return a function that returns an appropriate phrase for a given number.

    Args:
        singular: appropriate phrase for N=1.
        plural: appropriate phrase for N>1.
        zero: appropriate phrase for N=0. If None, uses plural.
        placeholder: string which will be replaced with the count when
            the selected phrase is returned. (Placeholder may simply be
            omitted from the phrases if not needed.)
    Returns:
        a function which returns the correct phrase for the count it is
        given.

    >>> phrase = pl('# failure', '# failures')
    >>> phrase(1)
    '1 failure'
    >>> phrase(5)
    '5 failures'
    >>> phrase(0)
    '0 failures'
    >>> phrase('two')
    'two failures'
    >>> phrase(1, word='one')
    'one failure'

    >>> phrase = pl('# failure', '# failures', zero='All passed!')
    >>> phrase(1)
    '1 failure'
    >>> phrase(5)
    '5 failures'
    >>> phrase(0)
    'All passed!'
    >>> n = 10; phrase(n, word=n if n < 5 else 'Too many')
    'Too many failures'

    >>> phrase = pl('one', 'more than one', zero='no')
    >>> phrase(1)
    'one'
    >>> phrase(5)
    'more than one'
    >>> phrase(0)
    'no'

    >>> phrase = pl(
    ...     "You're the best!",
    ...     "Y'all are the best!",
    ...     zero="Nobody here :(")
    >>> phrase(1)
    "You're the best!"
    >>> phrase(3)
    "Y'all are the best!"
    >>> phrase(0)
    'Nobody here :('

    >>> phrase = pl('# apple was bad', '# apples were bad')
    >>> phrase(1)
    '1 apple was bad'
    >>> phrase(1.5)
    '1.5 apples were bad'
    >>> phrase(3)
    '3 apples were bad'
    >>> phrase(0)
    '0 apples were bad'
    >>> n = 1; phrase(n, word=['no', 'a single', 'multiple'][n])
    'a single apple was bad'
    >>> n = 0; phrase(n, word=['no', 'a single', 'multiple'][n])
    'no apples were bad'
    """
    if zero is None:
        zero = plural

    def pluralizable(count, *, word=None):
        """Return an appropriate phrase based on the given count.

        Substitutes the placeholder with the count, or word if it is
        given (e.g., "one million", "too many").
        """
        if word is None:
            word = str(count)
        if count == 0:
            phrase = zero
        elif count == 1:
            phrase = singular
        else:
            phrase = plural
        return phrase.replace(placeholder, word)

    return pluralizable


if __name__ == '__main__':
    import doctest
    doctest.testmod()
