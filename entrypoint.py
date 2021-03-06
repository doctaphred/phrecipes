"""(WIP) A not-entirely-awful syntax for richly typed CLI arguments (and more!)

Args:

    >>> splitparse(''' ayy lmao ''')
    ('ayy', 'lmao')

Kwargs:

    >>> splitparse(''' ayy=lmao ''')  # doctest: +SKIP
    () {'ayy': 'lmao'}

Values without a ':'-delimited type prefix are ALWAYS strings:

    >>> splitparse(''' 1 1.0 True False None () [] {} ''')
    ('1', '1.0', 'True', 'False', 'None', '()', '[]', '{}')

Explicit type conversion:

    >>> splitparse(''' str:1 int:1 float:1 complex:1 utf8:1 str: utf8:''')
    ('1', 1, 1.0, (1+0j), b'1', '', b'')

Automatic (but still explicit) type conversion:

    >>> splitparse(''' :1 :1.0 :True :False :None :() :[] :{} ''')
    (1, 1.0, True, False, None, (), [], {})

For the QA enthusiasts (see also `PARSEPOS_EXAMPLES` below):

    >>> splitparse(''' :str: : :: ''')
    ('str:', '', ':')

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


class convert:
    str = str
    int = int
    float = float
    complex = complex

    from decimal import Decimal
    number = decimal = Decimal

    def auto(rep):
        """
        XXX: TODO: FIXME
        >>> ok =     '(' * 200 + '0' + ')' * 200
        >>> not_ok = '(' * 201 + '0' + ')' * 201
        >>> convert.auto(ok)
        0
        >>> convert.auto(not_ok)[:10]
        '(((((((((('
        """
        from ast import literal_eval
        try:
            return literal_eval(rep)
        except Exception:
            return rep

    def utf8(rep):
        """
        >>> convert.utf8('ayy')
        b'ayy'
        """
        return rep.encode('utf-8')

    def hexbytes(rep):
        r"""
        >>> convert.hexbytes('bad1d3a5')
        b'\xba\xd1\xd3\xa5'
        """
        return bytes.fromhex(rep)

    def hexint(rep):
        """
        >>> convert.hexint('bad1d3a5')
        3134313381
        >>> convert.hexint('0xbad1d3a5')
        3134313381
        """
        return int(rep, base=16)

    def octint(rep):
        """
        >>> convert.octint('1337')
        735
        >>> convert.octint('0o1337')
        735
        """
        return int(rep, base=8)

    def binint(rep):
        """
        >>> convert.binint('10')
        2
        >>> convert.binint('0b10')
        2
        """
        return int(rep, base=2)

    # TODO: Disallow negative values in hexint/octint/binint?


def parsepos(arg, *, typesep=':', conversions=vars(convert)):
    parts = arg.split(typesep, maxsplit=1)
    try:
        conv, rep = parts
    except ValueError:
        assert typesep not in arg
        # Positional args without ':' are just strings.
        return arg

    if not conv:
        assert arg.startswith(typesep)
        conv = 'auto'

    try:
        convert = conversions[conv]
    except KeyError:
        raise Exception(f"unknown conversion {conv!r}")

    try:
        return convert(rep)
    except Exception as exc:
        raise Exception(f"cannot convert {rep!r} to {conv!r}: {exc}")


PARSEPOS_EXAMPLES = r"""

Strings:

    ayy      'ayy'
    str:ayy  'ayy'
    :ayy     'ayy'


Constants:

    :True   True
    :False  False
    :None   None
    :...    Ellipsis


Integers:

    :0       0
    :1       1
    :+0      0
    :+1      1
    :-0      0
    :-1     -1

    int:0    0
    int:1    1
    int:+0   0
    int:+1   1
    int:-0   0
    int:-1  -1


Hexadecimal integers (with or without '0x' prefix):

    hexint:bad1d3a5    3134313381
    hexint:0xbad1d3a5  3134313381


Octal integers (with or without '0o' prefix):

    octint:1337    735
    octint:0o1337  735


Binary integers (with or without '0b' prefix):

    binint:10    2
    binint:0b10  2


(TODO: check for base prefixes in regular 'int' conversion.)


UTF-8 encoded bytes:

    utf8:ayy  b'ayy'
    utf8:     b''


Hex-encoded bytes:

    hexbytes:bad1d3a5  b'\xba\xd1\xd3\xa5'


(TODO: allow prefixes, support other bases (2, 8, 32, 64, 85?).)


Fixed-precision decimals:

    decimal:0     Decimal('0')
    decimal:1     Decimal('1')

    decimal:0.0   Decimal('0.0')
    decimal:1.0   Decimal('1.0')
    decimal:+0.0  Decimal('0.0')
    decimal:+1.0  Decimal('1.0')
    decimal:-0.0  Decimal('-0.0')
    decimal:-1.0  Decimal('-1.0')

    decimal:0.    Decimal('0')
    decimal:.0    Decimal('0.0')


Floats:

    :1.0         1.0
    :1.          1.0
    :0.0         0.0
    :0.          0.0
    :.0          0.0
    :+1.0        1.0
    :+1.         1.0
    :+0.0        0.0
    :+0.         0.0
    :+.0         0.0
    :-1.0       -1.0
    :-1.        -1.0
    :-.1        -0.1
    :-0.1       -0.1
    :.1          0.1
    :0.1         0.1
    :-0.0       -0.0
    :-0.        -0.0
    :-.0        -0.0
    :-00.0      -0.0
    :-0.00      -0.0

    float:1.0    1.0
    float:+1.0   1.0
    float:-1.0  -1.0
    float:1.     1.0
    float:+1.    1.0
    float:-1.   -1.0
    float:.1     0.1
    float:+.1    0.1
    float:-.1   -0.1
    float:0.0    0.0
    float:0.     0.0
    float:.0     0.0
    float:+0.0   0.0
    float:+0.    0.0
    float:+.0    0.0
    float:-0    -0.0
    float:-0.0  -0.0
    float:-.0   -0.0
    float:-0.   -0.0

    float:1      1.0
    float:0      0.0
    float:+1     1.0
    float:+0     0.0

    :1e0         1.0
    :1e1         10.0
    :1e10        10000000000.0
    :1e100       1e+100


TODO: should probably raise an exception for too-big values:

    :+1e308  1e+308
    :-1e308  -1e+308
    :+2e308  inf
    :-2e309  -inf

(Or just parse as decimals by default?)

    decimal:1e308  Decimal('1E+308')
    decimal:2e308  Decimal('2E+308')


Special floats:

    float:nan   nan
    float:Nan   nan
    float:NaN   nan
    float:NAN   nan

    float:inf   inf
    float:Inf   inf
    float:INF   inf
    float:+inf   inf
    float:+Inf   inf
    float:+INF   inf

    float:-inf -inf
    float:-Inf -inf
    float:-INF -inf


Tricky strings that look like special floats:

    :nan  'nan'
    :inf  'inf'
    :-inf '-inf'

(TODO: Should these actually be parsed as floats?)


Complex numbers:

    :1+0j   (1+0j)
    :(1+0j) (1+0j)
    :1+1j   (1+1j)
    :1j        1j
    :+1j       1j
    :0j        0j
    :0+1j      1j
    :(1j)      1j
    :(0j)      0j


Values are never implicitly converted without a prefix:

    0      '0'
    +1      '+1'
    -0.1   '-0.1'
    True   'True'
    False  'False'
    None   'None'
    ...    '...'


Tricky strings:

    :            ''
    str:         ''

    ::           ':'
    str::        ':'

    str          'str'
    :str         'str'
    str:str      'str'

    :str:        'str:'
    str:str:     'str:'
    str:str:str  'str:str'
    :str:str     'str:str'
    ::str        ':str'
    str::str     ':str'


Tricky strings that look like integers:

    :01    '01'
    :-01  '-01'


Extra tricky *integers* that look like tricky strings that look like integers:

    :00     0
    :-00    0

(TODO: Should probably change or disallow those...)


Complex numbers which are *not* valid complex literals:

    complex:1      (1+0j)
    complex:0         0j
           :1       1
           :0       0

    complex:1.0    (1+0j)
    complex:0.0       0j
           :1.0     1.0
           :0.0     0.0

    complex:j         1j
    complex:+j        1j
    complex:-j       -1j
           :j         'j'
           :+j       '+j'
           :-j       '-j'

    complex:0+j       1j
           :0+j     '0+j'

    complex:(0j)       0j
           :(0j)       0j

    complex:(1+j)  (1+1j)
           :(1+j)  '(1+j)'

    complex:1+j    (1+1j)
           :1+j     '1+j'


Tricky strings that look like complex numbers:

    1+0j   '1+0j'
    (1+0j) '(1+0j)'
    1+j    '1+j'
    j      'j'
    +j     '+j'

    :01+0j   '01+0j'
    :(01+0j) '(01+0j)'
    :01+1j   '01+1j'
    :0+j     '0+j'


Malformed complex numbers which raise an exception when parsed:

    complex:j+1
    complex:i


Tricky values with disappearing parentheses:

    :(0)    0
    :(1)    1
    :(+0)   0
    :(+1)   1
    :(-0)   0
    :(-1)  -1
    :(((...)))  Ellipsis

(TODO: Should probably stop using `ast.literal_eval`...)

"""


if __debug__:
    class test:
        errors = []
        for line in PARSEPOS_EXAMPLES.splitlines():
            if line.startswith('    '):
                example = line.strip()
                try:
                    case, expected_repr = example.split(maxsplit=1)
                except ValueError:
                    case, expected_repr = example, None
                try:
                    actual = parsepos(case)
                except Exception as exc:
                    if expected_repr is not None:
                        errors.append(
                            f"Unexpected exception in example {case!r}:"
                            f" {exc.__class__.__name__}: {exc}")
                else:
                    if expected_repr is None:
                        errors.append(
                            f"Failed example {case!r}:"
                            f" expected exception, got {actual!r}")
                    elif repr(actual) != expected_repr:
                        errors.append(
                            f"Failed example {case!r}:"
                            f" expected {expected_repr}, got {actual!r}")
        if errors:
            raise SystemExit('\n'.join(errors))
