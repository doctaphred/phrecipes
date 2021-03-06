import re
from collections import namedtuple


def lines(text, *, pattern=re.compile(r'^.*$', flags=re.MULTILINE)):
    r"""Yield lines of text, one at a time.

    >>> list(lines('ayy\nlmao'))
    ['ayy', 'lmao']

    >>> list(lines('\nayy\n\nlmao\n'))
    ['', 'ayy', '', 'lmao', '']
    """
    scanner = pattern.scanner(text)
    for match in iter(scanner.search, None):
        yield match.group()


def trim(text, *, pattern=re.compile(r'^( *)(.*?)( *)$', flags=re.DOTALL)):
    r"""Separate out leading and trailing spaces, and return a 3-tuple.

    NOTE: Tabs and other whitespace characters are NOT trimmed; just spaces.

    >>> trim('ayy lmao')
    ('', 'ayy lmao', '')

    >>> trim(' ayy lmao ')
    (' ', 'ayy lmao', ' ')

    >>> trim(' \t\r\n ')
    (' ', '\t\r\n', ' ')

    >>> trim('    ')
    ('    ', '', '')

    >>> trim('')
    ('', '', '')
    """
    return pattern.fullmatch(text).groups()


def trim_lines(text, *,
               pattern=re.compile(r'^( *)(.*?)( *)$', flags=re.MULTILINE)):
    r"""Yield 3-tuples of lines with leading and trailing spaces separated out.

    NOTE: Tabs and other whitespace characters are NOT trimmed; just spaces.

    >>> list(trim_lines('ayy lmao'))
    [('', 'ayy lmao', '')]

    >>> list(trim_lines(' ayy lmao '))
    [(' ', 'ayy lmao', ' ')]

    >>> list(trim_lines(' ayy\nlmao '))
    [(' ', 'ayy', ''), ('', 'lmao', ' ')]

    >>> list(trim_lines(''))
    [('', '', '')]

    >>> list(trim_lines('\n'))
    [('', '', ''), ('', '', '')]

    >>> list(trim_lines('\t\r\n'))
    [('', '\t\r', ''), ('', '', '')]
    """
    scanner = pattern.scanner(text)
    for match in iter(scanner.search, None):
        yield match.groups()


class Token(namedtuple('Token', ['kind', 'value', 'start', 'end'])):
    __slots__ = ()

    @classmethod
    def from_match(cls, match):
        return cls(match.lastgroup, match.group(), *match.span())

    @property
    def loc(self):
        return self.start + 1


class QuotedListTokenizer:
    r"""Tokenizer for QuotedListParser.

    >>> show = QuotedListTokenizer().show

    >>> show('ayy lmao')
    other: 'ayy'
    sep: ' '
    other: 'lmao'

    >>> show(' ayy    lmao ')
    sep: ' '
    other: 'ayy'
    sep: '    '
    other: 'lmao'
    sep: ' '

    >>> show('"ayy" "lmao"')
    quote: '"'
    other: 'ayy'
    quote: '"'
    sep: ' '
    quote: '"'
    other: 'lmao'
    quote: '"'

    >>> show(r'"ayy\"lmao"')
    quote: '"'
    other: 'ayy'
    escape: '\\"'
    other: 'lmao'
    quote: '"'
    """

    def __init__(self, *, sep=' ', quote='"', escape='\\'):
        self.sep = sep
        self.quote = quote
        self.escape = escape

        sep = re.escape(sep)
        quote = re.escape(quote)
        escape = re.escape(escape)

        self.pattern = re.compile(
            '|'.join([
                # French strings, hon hon hon
                fr'(?P<sep>{sep}+)',
                fr'(?P<quote>{quote})',
                fr'(?P<escape>{escape}.)',  # Includes the escaped character.
                fr'(?P<other>[^{sep}{quote}{escape}]+)',
            ]),
            flags=re.DOTALL,
        )

    def __call__(self, text):
        scanner = self.pattern.scanner(text)
        for match in iter(scanner.search, None):
            yield Token.from_match(match)

    def show(self, text):
        for token in self(text):
            print(f"{token.kind}: {token.value!r}")


class QuotedListParser:
    r"""Split text on on a separator character, observing quotes and escapes.

    >>> show = QuotedListParser.show

    Text is split into items on the separator character.
    >>> show('ayy lmao')
    'ayy'
    'lmao'

    Quotes preserve the separator character.
    >>> show('" ayy    lmao "')
    ' ayy    lmao '

    Empty quotes represent an empty item.
    >>> show(' ayy "" lmao ')
    'ayy'
    ''
    'lmao'

    Leading, trailing, and repeated separator characters are ignored.
    >>> show(' ayy    lmao ')
    'ayy'
    'lmao'

    The quote character may be escaped within a quote.
    >>> show('"~"ayy~" ~"lmao~""', escape='~')
    '"ayy" "lmao"'

    The escape character may be escaped within a quote.
    >>> show('"~~~"ayy~~~" ~~~"lmao~~~""', escape='~')
    '~"ayy~" ~"lmao~"'

    Unescaped quote characters must occur in pairs.
    >>> show('ayy "lmao')
    Traceback (most recent call last):
      ...
    Exception: unmatched quote at column 5

    Escape sequences may only be used within quotes.
    >>> show('ayy ~"lmao~"', escape='~')
    Traceback (most recent call last):
      ...
    Exception: unquoted escape sequence at column 5

    Only the quote and escape characters may be escaped.
    >>> show('"ayy~ lmao"', escape='~')
    Traceback (most recent call last):
      ...
    Exception: invalid escape character ' ' at column 6

    """
    Scanner = QuotedListTokenizer

    def __init__(self, text, **kwargs):
        self.text = text
        self.scanner = self.Scanner(**kwargs)
        self.tokens = self.scanner(text)

    def line(self):
        for token in self.tokens:
            if token.kind == 'sep':
                pass
            elif token.kind == 'quote':
                assert token.value == self.scanner.quote
                yield self.quote(token)
            elif token.kind == 'escape':
                raise Exception(
                    f"unquoted escape sequence at column {token.loc}")
            else:
                yield token.value

    __iter__ = line

    def quote(self, open_quote_token):
        quote = []
        for token in self.tokens:
            if token.kind == 'quote':
                assert token.value == self.scanner.quote
                return ''.join(quote)
            elif token.kind == 'escape':
                quote.append(self.escape(token))
            else:
                quote.append(token.value)
        raise Exception(f"unmatched quote at column {open_quote_token.loc}")

    def escape(self, token):
        escape, char = token.value
        assert escape == self.scanner.escape
        if char == self.scanner.escape:
            return char
        elif char == self.scanner.quote:
            return char
        else:
            raise Exception(
                f"invalid escape character {char!r} at column {token.loc + 1}")

    @classmethod
    def show(cls, text, **kwargs):
        self = cls(text, **kwargs)
        for item in self:
            print(repr(item))
