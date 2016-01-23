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

    See also plfmt for slightly less typing in simpler cases.

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


def plfmt(__phrase__, *, __count__='#', s='', es='', **singularizations):
    """Enclose the phrase in a function which can pluralize it.

    __phrase__ and __count__ are "dundered" because 'phrase' and
    'count' are both valid pluralizable words.

    Args:
        __phrase__: the phrase to pluralize.
        __count__: the key to insert the count into the pluralized form.
        s: what '{s}' should be replaced with.
        es: what '{es}' should be replaced with'.
        singularizations: plural words mapped to their singular forms.
    Returns:
        a function which returns a correctly-pluralized rendering of
        __phrase__, according to the count given to it.

    >>> phrase = plfmt('{#} dollar{s}')
    >>> phrase(0)
    '0 dollars'
    >>> phrase(1)
    '1 dollar'
    >>> phrase('1')
    '1 dollar'
    >>> phrase(1.0)
    '1.0 dollars'
    >>> phrase(1.0, pluralize=1.0 != 1)
    '1.0 dollar'
    >>> phrase('One', pluralize=str('One').casefold() not in {'1', 'one'})
    'One dollar'
    >>> phrase(2)
    '2 dollars'
    >>> phrase('one million')
    'one million dollars'

    >>> phrase = plfmt('{#} apple{s} had {worms}', worms='a worm')
    >>> phrase(0)
    '0 apples had worms'
    >>> phrase(1)
    '1 apple had a worm'
    >>> phrase(2)
    '2 apples had worms'
    >>> phrase(0.1)
    '0.1 apples had worms'
    >>> phrase('zero')
    'zero apples had worms'
    >>> phrase('one', pluralize=False)
    'one apple had a worm'
    >>> phrase('two')
    'two apples had worms'
    >>> phrase('too many')
    'too many apples had worms'
    >>> phrase('only one')
    'only one apples had worms'
    >>> phrase('only one', pluralize=False)
    'only one apple had a worm'

    >>> phrase = plfmt("{These} {are} real treat{s}!", These='This', are='is a')
    >>> phrase(1)
    'This is a real treat!'
    >>> phrase(2)
    'These are real treats!'

    >>> phrase = plfmt("{Y'all}{ are }the best!", **{"Y'all": "You", ' are ': "'re "})
    >>> phrase(1)
    "You're the best!"
    >>> phrase(2)
    "Y'all are the best!"

    For complex cases like the last two examples, consider using
    pl instead.
    """
    singularizations = {'s': s, 'es': es, **singularizations}

    def pluralizable(count, *, pluralize=None):
        count_replacement = {__count__: count}

        if pluralize is None:
            pluralize = str(count) != '1'

        if pluralize:
            return __phrase__.format_map(KeyReplacer(count_replacement))
        return __phrase__.format(**singularizations, **count_replacement)

    return pluralizable


if __name__ == '__main__':
    import doctest
    doctest.testmod()
