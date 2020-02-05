class SingleLineSanitizer(dict):
    r"""Sanitize a string for output on a single line.

    Use with `str.translate`, or call an instance.

        >>> cls = SingleLineSanitizer
        >>> s = cls()

        >>> 'ayy\nlmao'.translate(s)
        'ayy␊lmao'

        >>> s('ayy\nlmao')
        'ayy␊lmao'

    Commonly used control characters are replaced with symbols:

        >>> s('\a\b\f\n\r\t\v\x00\x1b\x7f')
        '␇␈␌␊␍␉␋␀␛␡'

    Other control characters (except `U+0020 SPACE`), marks, and
    separators are replaced with `U+FFFD REPLACEMENT CHARACTER`:

        >>> s('ayy\x01lmao')
        'ayy�lmao'
        >>> s('ayy\N{combining ligature left half below}lmao')
        'ayy�lmao'
        >>> s('ayy\N{no-break space}lmao')
        'ayy�lmao'

    To avoid ambiguity, symbols used as replacements are themselves
    replaced with the replacement character:

        >>> s('␇␈␌␊␍␉␋␀␛␡')
        '����������'

    The replacement character itself is not replaced by default:

        >>> s('ayy\N{replacement character}lmao')
        'ayy�lmao'

    Behavior can be customized in several ways:

        >>> 'ayy lmao'.translate(cls({' ': '\N{symbol for space}'}))
        'ayy␠lmao'

        >>> 'ayy lmao'.translate(cls({' ': '\N{middle dot}'}))
        'ayy·lmao'

        >>> 'ayy\x01lmao'.translate(cls(replacement='\N{pile of poo}'))
        'ayy💩lmao'

        >>> 'ayy�lmao'.translate(
        ...     cls(
        ...         forbidden=lambda c: c == '�',
        ...         replacement='\N{face with no good gesture}'))
        'ayy🙅lmao'

        >>> '�🤔'.translate(cls())
        '�🤔'

        >>> '�🤔'.translate(cls({'�': '🤔'}))
        '🤔�'

        >>> '�🤔'.translate(cls({'�': '🤔'}, replacement='🤷'))
        '🤔🤷'

    """
    replacement = '\N{replacement character}'  # �

    defaults = {
        '\a': '␇',  # terminal bell (BEL)
        '\b': '␈',  # backspace (BS)
        '\f': '␌',  # form feed (FF)
        '\n': '␊',  # linefeed (LF)
        '\r': '␍',  # carriage return (CR)
        '\t': '␉',  # horizontal tab (TAB)
        '\v': '␋',  # vertical tab (VT)
        '\x00': '␀',  # null (NUL)
        '\x1b': '␛',  # escape (ESC)
        '\x7f': '␡',  # delete (DEL)
        ' ': ' ',  # Space is a control character: whitelist it.
        # TODO: replace non-U+0020 space characters with '\N{middle dot}'/'·'?
    }

    forbidden_categories = {
        'Cc',  # Other, Control
        'Cf',  # Other, Format
        'Cn',  # Other, Not Assigned
        'Co',  # Other, Private Use
        'Cs',  # Other, Surrogate
        # 'LC',  # Letter, Cased
        # 'Ll',  # Letter, Lowercase
        # 'Lm',  # Letter, Modifier
        # 'Lo',  # Letter, Other
        # 'Lt',  # Letter, Titlecase
        # 'Lu',  # Letter, Uppercase
        'Mc',  # Mark, Spacing Combining
        'Me',  # Mark, Enclosing
        'Mn',  # Mark, Nonspacing
        # 'Nd',  # Number, Decimal Digit
        # 'Nl',  # Number, Letter
        # 'No',  # Number, Other
        # 'Pc',  # Punctuation, Connector
        # 'Pd',  # Punctuation, Dash
        # 'Pe',  # Punctuation, Close
        # 'Pf',  # Punctuation, Final quote
        # 'Pi',  # Punctuation, Initial quote
        # 'Po',  # Punctuation, Other
        # 'Ps',  # Punctuation, Open
        # 'Sc',  # Symbol, Currency
        # 'Sk',  # Symbol, Modifier
        # 'Sm',  # Symbol, Math
        # 'So',  # Symbol, Other
        'Zl',  # Separator, Line
        'Zp',  # Separator, Paragraph
        'Zs',  # Separator, Space
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args)
        vars(self).update(kwargs)

    def __getitem__(self, key):
        # str.translate passes an integer: convert it to a string.
        return super().__getitem__(chr(key))

    def __missing__(self, char):
        # __getitem__ has already converted the key to a string.
        if char in self.defaults:
            return self.defaults[char]
        elif self.forbidden(char):
            return self.replacement
        else:
            return char

    def forbidden(self, char):
        if char in self.values():
            return True
        elif char in self.defaults.values():
            return True
        else:
            from unicodedata import category
            return category(char) in self.forbidden_categories

    def __call__(self, obj):
        return str(obj).translate(self)
