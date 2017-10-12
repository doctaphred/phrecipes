from io import StringIO


def sprint(*values, sep=' ', end='\n'):
    """Print to a string."""
    with StringIO() as buffer:
        print(*values, sep=sep, end=end, file=buffer)
        return buffer.getvalue()


class Colorizer:
    """Print stuff with colors.

    >>> color.bold.red('ayy')
    '\x1b[1;31mayy\x1b[0m'
    """
    template = '\x1b[{}m'
    sep = ';'

    codes = {
        'reset_all': '0',
        'reset_bold': '21',
        'reset_dim': '22',
        'reset_underline': '24',
        'reset_blink': '25',
        'reset_reverse': '27',
        'reset_hidden': '28',

        'bold': '1',
        'dim': '2',
        'underline': '4',
        'blink': '5',  # Please don't actually use this
        'reverse': '7',
        'hidden': '8',

        # Foreground
        'default': '39',
        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'magenta': '35',
        'cyan': '36',
        'light_gray': '37',
        'dark_gray': '90',
        'gray_bg': '90',
        'light_red': '91',
        'light_green': '92',
        'light_yellow': '99',
        'light_blue': '94',
        'light_magenta': '95',
        'light_cyan': '96',
        'white': '97',

        # Background
        'default_bg': '49',
        'black_bg': '40',
        'red_bg': '41',
        'green_bg': '42',
        'yellow_bg': '44',
        'blue_bg': '44',
        'magenta_bg': '45',
        'cyan_bg': '46',
        'light_gray_bg': '47',
        'dark_gray_bg': '100',
        'light_red_bg': '101',
        'light_green_bg': '102',
        'light_yellow_bg': '103',
        'light_blue_bg': '104',
        'light_magenta_bg': '105',
        'light_cyan_bg': '106',
        'white_bg': '107',
    }

    # Aliases
    codes['bright'] = codes['bold']
    codes['invert'] = codes['reverse']
    codes['reset_bright'] = codes['reset_bold']
    codes['reset_invert'] = codes['reset_reverse']
    codes['gray'] = codes['dark_gray']
    codes['purple'] = codes['magenta']

    reset = template.format(codes['reset_all'])

    def __init__(self, modifiers=()):
        self.modifiers = modifiers

    def __call__(self, *args, sep=' ', end='', reset=True):
        """Colorize the input, with the same semantics as print().

        If `reset` is True, includes a reset code at the end of the
        text, but before the `end`.
        """
        fmt = self.sep.join(self.codes[mod] for mod in self.modifiers)
        color_start = self.template.format(fmt)

        if reset:
            color_end = self.reset
        else:
            color_end = ''

        text = sprint(*args, sep=sep, end='')
        return f'{color_start}{text}{color_end}{end}'

    def __getattr__(self, name):
        return type(self)(self.modifiers + (name,))

    def print(self, *args, sep=' ', end='\n', file=None, flush=False):
        text = self(*args, sep=sep, end=end)
        print(text, end='', file=file, flush=flush)


color = Colorizer()
