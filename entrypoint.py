"""(WIP) A not-entirely-awful serialization syntax.

Args:

    >>> splitparse(''' ayy lmao ''')
    ('ayy', 'lmao')

Kwargs:

    >>> splitparse(''' ayy=lmao ''')  # doctest: +SKIP
    () {'ayy': 'lmao'}

Explicit type conversion:

    >>> splitparse(''' str:1 int:1 float:1 complex:1 utf8:1 str: utf8:''')
    ('1', 1, 1.0, (1+0j), b'1', '', b'')

Automatic type conversion:

    >>> splitparse(''' :1 :1.0 :True :False :None :str: : :: ''')
    (1, 1.0, True, False, None, 'str:', '', ':')

Compound objects:

    >>> splitparse(''' :1,2,3 :,ayy,,lmao, ''')  # doctest: +SKIP
    ([1, 2, 3], ['', 'ayy', '', 'lmao', ''])

Name lookup:

    >>> foo, bar = 'ayy', 'lmao'  # doctest: +SKIP
    >>> splitparse(''' .foo .bar ''')  # doctest: +SKIP
    ('ayy', 'lmao')

Function calls:

    >>> splitparse(''' @len ayy ''')  # doctest: +SKIP
    (3,)

    >>> splitparse(''' @list @range :2: :7 step=:2 ''')  # doctest: +SKIP
    ([2, 4, 6],)

    >>> class x:  # doctest: +SKIP
    ...     foo = 'ayy'
    ...     @classmethod
    ...     def bar(cls):
    ...         return 'lmao'
    >>> splitparse(''' .x.foo @x.bar ''')  # doctest: +SKIP
    ['ayy', 'lmao']

Edge cases:

    >>> splitparse(''' str:ayy str:lmao ''')
    ('ayy', 'lmao')

    >>> splitparse(''' str:ayy=lmao ''')  # doctest: +SKIP
    ('ayy=lmao',)

    >>> splitparse(''' str:ayy=str:lmao ''')  # doctest: +SKIP
    >>> splitparse(''' str:ayy=str:lmao ''')  # doctest: +SKIP

    >>> splitparse('')
    ()

"""


def splitparse(line):
    import shlex
    return parse(shlex.split(line))


def parse(args):
    return tuple(map(parsepos, args))


def auto(rep):
    from ast import literal_eval
    try:
        return literal_eval(rep)
    except Exception:
        return rep


def utf8(rep):
    return rep.encode('utf-8')


conversions = {
    f.__name__: f for f in [str, int, float, complex, utf8]
}


def parsepos(arg, *, typesep=':', auto=auto, conversions=conversions):
    """
    >>> parsepos('ayy')
    'ayy'
    >>> parsepos('str:ayy')
    'ayy'
    >>> parsepos(':ayy')
    'ayy'
    >>> parsepos('str:str:ayy')
    'str:ayy'

    >>> parsepos('1')
    '1'
    >>> parsepos('str:1')
    '1'
    >>> parsepos('int:1')
    1
    >>> parsepos(':1')
    1

    >>> parsepos(':1.0')
    1.0
    >>> parsepos(':1.')
    1.0

    >>> parsepos('utf8:ayy')
    b'ayy'
    >>> parsepos('utf8:')
    b''

    >>> parsepos('float:0')
    0.0
    >>> parsepos('float:-0')
    -0.0
    >>> parsepos('float:nan')
    nan
    >>> parsepos('float:inf')
    inf
    >>> parsepos('float:-inf')
    -inf

    >>> parsepos(':nan')
    'nan'
    >>> parsepos(':inf')
    'inf'
    >>> parsepos(':-inf')
    '-inf'

    >>> parsepos('complex:1')
    (1+0j)
    >>> parsepos('complex:j')
    1j
    >>> parsepos('complex:+j')
    1j

    >>> parsepos('')
    ''
    >>> parsepos(':')
    ''
    >>> parsepos('::')
    ':'
    >>> parsepos('str:')
    ''
    >>> parsepos(':str:')
    'str:'

    >>> parsepos(':True')
    True
    >>> parsepos(':False')
    False
    >>> parsepos(':None') is None
    True

    """
    parts = arg.split(typesep, maxsplit=1)
    try:
        conv, rep = parts
    except ValueError:
        assert typesep not in arg
        return arg

    if not conv:
        assert arg.startswith(typesep)
        convert = auto
    else:
        try:
            convert = conversions[conv]
        except KeyError:
            raise Exception(f"unknown conversion {conv!r}")

    try:
        return convert(rep)
    except Exception:
        raise Exception(f"cannot convert {rep!r} to {conv!r}")
