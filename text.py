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
