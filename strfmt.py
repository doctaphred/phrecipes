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


def pl(*phrases, zero=None, placeholder='#'):
    """Return a function that returns an appropriate phrase for a given number.

    Args:
        phrases: appropriate phrases for N == 1, 2, etc.
            If N >= len(phrases), phrases[-1] will be selected.
        zero: appropriate phrase for N = 0. If zero is None and N == 0,
            phrases[-1] will be selected.
        placeholder: string which will be replaced with the count when
            the selected phrase is returned.
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

    >>> phrase = pl('one', 'two', 'several', zero='no')
    >>> phrase(1)
    'one'
    >>> phrase(2)
    'two'
    >>> phrase(5)
    'several'
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

    >>> phrase = pl(
    ...     'One is far too few, although with it thou must start.',
    ...     'Neither count thou two, excepting that thou then proceed to three.',
    ...     'Thou shalt count to three, no more, no less.',
    ...     'Four shalt thou not count.',
    ...     'Five is right out.',
    ...     'Wast thou even paying attention? If five is right out, what is #?',
    ...     zero='Ist that even a counting number?')
    >>> phrase(3)
    'Thou shalt count to three, no more, no less.'
    >>> phrase(4)
    'Four shalt thou not count.'
    >>> phrase(2)
    'Neither count thou two, excepting that thou then proceed to three.'
    >>> phrase(5)
    'Five is right out.'
    >>> phrase(100)
    'Wast thou even paying attention? If five is right out, what is 100?'
    >>> phrase(0)
    'Ist that even a counting number?'
    """
    default = phrases[-1]
    if zero is None:
        zero = default
    phrases = (zero,) + phrases

    def pluralizable(count, *, word=None):
        """Return an appropriate phrase based on the given count.

        Substitutes the placeholder with the count, or word if it is
        given (e.g., "one million").
        """
        if word is None:
            word = str(count)
        try:
            phrase = phrases[count]
        except (IndexError, TypeError):
            # Treat floats, strings, etc. as plural
            phrase = default
        return phrase.replace(placeholder, word)

    return pluralizable


if __name__ == '__main__':
    import doctest
    doctest.testmod()
