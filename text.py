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
