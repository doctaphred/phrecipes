import sys

from coolections import subdict
from magic import magic


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


@magic
class show:
    """
    >>> x = '''ayy
    lmao'''
    >>> show.x
    x = 'ayy\nlmao'
    """
    def __getattr__(self, name):
        value = sys._getframe(1).f_locals[name]
        print('{} = {!r}'.format(name, value))

    def __call__(self, *exclude):
        f_locals = sys._getframe(1).f_locals
        for name in sorted(f_locals):
            if name not in exclude:
                print('{} = {!r}'.format(name, f_locals[name]))


def vars_repr(obj, var_names=None, var_filter=None):
    """Return a repr string from the specified instance attributes.

    If no names are specified, uses all vars.

    >>> class Thing:
    ...     not_a_var = 'vars are instance attrs; this is a class attr'
    ...     def __init__(self, **kwargs):
    ...         self.__dict__.update(kwargs)
    ...     __repr__ = vars_repr

    >>> Thing(a=1, b=2)
    Thing(a=1, b=2)

    >>> vars_repr(Thing(a=1, b=2), ['a', 'bogus'])
    'Thing(a=1)'
    """
    repr_vars = subdict(vars(obj), keys=var_names, item_filter=var_filter)
    return '{}({})'.format(obj.__class__.__name__, argstr(**repr_vars))


def attr_repr(obj, attr_names=None):
    """Return a repr string from the specified attributes.

    If no attributes are specified, uses all "public" attributes
    (names that don't begin with an underscore).

    >>> class Thing:
    ...     a = 1
    ...     def __init__(self):
    ...         self.b = 2
    ...     @property
    ...     def c(self):
    ...         return 3
    ...     def method(self):
    ...         return 4
    ...     def __repr__(self):
    ...         return attr_repr(self, ['a', 'b', 'c'])

    >>> Thing()
    Thing(a=1, b=2, c=3)
    """
    if attr_names is None:
        attr_names = [name for name in dir(obj) if not name.startswith('_')]
    attrs = {name: getattr(obj, name) for name in attr_names}
    return '{}({})'.format(obj.__class__.__name__, argstr(**attrs))


def argstr(*args, **kwargs):
    """Return a string representation of the given signature.

    Lists kwargs in sorted order.

    >>> argstr(1, 2, 3)
    '1, 2, 3'
    >>> argstr()
    ''
    >>> argstr(a=1)
    'a=1'
    >>> argstr(1, 2, c=3)
    '1, 2, c=3'
    >>> argstr(a=1, c=3, b=2)
    'a=1, b=2, c=3'
    """
    if not args and not kwargs:
        return ''

    args_str = ', '.join(repr(arg) for arg in args)
    kwargs_str = ', '.join('{}={!r}'.format(k, v)
                           for k, v in sorted(kwargs.items()))

    if not args:
        return kwargs_str
    if not kwargs:
        return args_str
    return '{}, {}'.format(args_str, kwargs_str)


def callstr(obj, *args, **kwargs):
    """Return a string representation of a call to the given object.

    >>> callstr('ayy', 'lm', a='o')
    "ayy('lm', a='o')"
    """
    return '{}({})'.format(obj, argstr(*args, **kwargs))


def count(items, singular, plural=None, zero=None, *, suffix='s'):
    """Return a properly pluralized string representing the number of items.

    >>> one, two, zero = 'a', 'aa', ''

    >>> count(one, 'apple')
    '1 apple'
    >>> count(two, 'apple')
    '2 apples'
    >>> count(zero, 'apple')
    '0 apples'

    >>> count(one, 'octopus')
    '1 octopus'
    >>> count(two, 'octopus', suffix='es')
    '2 octopuses'
    >>> count(two, 'octopus', 'octopi')
    '2 octopi'
    >>> count(zero, 'octopus', 'octopi', zero='octopi (whew!)')
    '0 octopi (whew!)'
    """
    if plural is None:
        plural = singular + suffix
    if zero is None:
        zero = plural

    n = len(items)
    if n == 0:
        word = zero
    elif n == 1:
        word = singular
    else:
        word = plural
    return '{} {}'.format(n, word)


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
