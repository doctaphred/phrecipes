Extended doctests for ``parse``
===============================

..
    >>> from parse import *


``QuotedListParser``
--------------------

    >>> show = QuotedListParser.show


    >>> show('""')
    ''

    >>> show('"~~"', escape='~')
    '~'

    >>> show('"~""', escape='~')
    '"'

    >>> show('')

    >>> show(' ')


Quoted text
~~~~~~~~~~~

    >>> show('"ayy" lmao')
    'ayy'
    'lmao'

    >>> show('ayy "lmao"')
    'ayy'
    'lmao'

    >>> show('"ayy" "lmao"')
    'ayy'
    'lmao'

    >>> show(' "ayy" "lmao" ')
    'ayy'
    'lmao'

    TODO: require spaces around quotes.
    >>> show('"ayy"lmao')
    'ayy'
    'lmao'


Unmatched quotes
~~~~~~~~~~~~~~~~

    >>> show('ayy "lmao')
    Traceback (most recent call last):
      ...
    Exception: unmatched quote at column 5


Escape sequences
~~~~~~~~~~~~~~~~

    >>> show(r'ayy \"lmao\"')
    Traceback (most recent call last):
      ...
    Exception: unquoted escape sequence at column 5

    >>> show('ayy\ lmao')
    Traceback (most recent call last):
      ...
    Exception: unquoted escape sequence at column 4

    >>> show('"ayy\ lmao"')
    Traceback (most recent call last):
      ...
    Exception: invalid escape character ' ' at column 6

