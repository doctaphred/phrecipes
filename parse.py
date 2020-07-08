import re


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


class QuoteScanner:
    r"""Tokenizer for QuoteSplitter.

    >>> scan = QuoteScanner().show

    >>> scan('ayy lmao')
    other: 'ayy'
    delimiter: ' '
    other: 'lmao'

    >>> scan(' ayy    lmao ')
    delimiter: ' '
    other: 'ayy'
    delimiter: '    '
    other: 'lmao'
    delimiter: ' '

    >>> scan('"ayy" "lmao"')
    quote: '"'
    other: 'ayy'
    quote: '"'
    delimiter: ' '
    quote: '"'
    other: 'lmao'
    quote: '"'

    >>> scan(r'"ayy\"lmao"')
    quote: '"'
    other: 'ayy'
    escape: '\\"'
    other: 'lmao'
    quote: '"'
    """
    def __init__(self, *, delimiter=' ', quote='"', escape='\\'):
        self.delimiter = delimiter
        self.quote = quote
        self.escape = escape

        delimiter = re.escape(delimiter)
        quote = re.escape(quote)
        escape = re.escape(escape)

        self.pattern = re.compile(
            '|'.join([
                # French strings, hon hon hon
                fr'(?P<delimiter>{delimiter}+)',
                fr'(?P<quote>{quote})',
                fr'(?P<escape>{escape}.)',  # Includes the escaped character.
                fr'(?P<other>[^{delimiter}{quote}{escape}]+)',
            ]),
            flags=re.DOTALL,
        )

    def __call__(self, text):
        scanner = self.pattern.scanner(text)
        for match in iter(scanner.search, None):
            yield match.lastgroup, match.group()

    def show(self, text):
        for kind, value in self(text):
            print(f"{kind}: {value!r}")


class QuoteSplitter:
    r"""Split text on on a delimiter character, observing quotes and escapes.

    >>> list(QuoteSplitter('ayy lmao'))
    ['ayy', 'lmao']

    >>> list(QuoteSplitter(' ayy lmao '))
    ['ayy', 'lmao']

    >>> list(QuoteSplitter('"ayy" "lmao"'))
    ['ayy', 'lmao']

    >>> list(QuoteSplitter('"ayy lmao"'))
    ['ayy lmao']

    >>> list(QuoteSplitter(r'"\"ayy\" \"lmao\""'))
    ['"ayy" "lmao"']

    >>> list(QuoteSplitter('ayy "lmao'))
    Traceback (most recent call last):
      ...
    Exception: unmatched quote

    >>> list(QuoteSplitter('ayy\ lmao'))
    Traceback (most recent call last):
      ...
    Exception: unquoted escape sequence

    >>> list(QuoteSplitter('"ayy\ lmao"'))
    Traceback (most recent call last):
      ...
    Exception: invalid escape character ' '
    """
    Scanner = QuoteScanner

    def __init__(self, text, **kwargs):
        self.text = text
        self.scanner = self.Scanner(**kwargs)
        self.tokens = self.scanner(text)

    def line(self):
        for kind, value in self.tokens:
            if kind == 'delimiter':
                pass
            elif kind == 'quote':
                yield self.quote()
            elif kind == 'escape':
                raise Exception("unquoted escape sequence")
            else:
                yield value

    __iter__ = line

    def quote(self):
        quote = []
        for kind, value in self.tokens:
            if kind == 'quote':
                return ''.join(quote)
            elif kind == 'escape':
                escape, char = value
                assert escape == self.scanner.escape
                quote.append(self.escape(char))
            else:
                quote.append(value)
        raise Exception("unmatched quote")

    def escape(self, char):
        if char != self.scanner.quote:
            raise Exception(f"invalid escape character {char!r}")
        return char
