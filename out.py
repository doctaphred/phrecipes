from functools import partial
from io import StringIO


def sprint(*values, sep=' ', end='\n'):
    """Print to a string."""
    with StringIO() as buffer:
        print(*values, sep=sep, end=end, file=buffer)
        return buffer.getvalue()


@object.__new__
class color:
    """Print stuff with colors.

    >>> color.bold_red('ayy')
    '\x1b[1;31mayy\x1b[0m'
    """

    template = '\x1b[{}m'
    sep = ';'

    codes = {
        'reset': '0',
        'bold': '1',
        'underline': '4',
        'invert': '7',

        'black': '30',
        'red': '31',
        'green': '32',
        'yellow': '33',
        'blue': '34',
        'purple': '35',
        'cyan': '36',
        'gray': '37',
        'white': '37',

        'bgblack': '40',
        'bgred': '41',
        'bggreen': '42',
        'bgyellow': '44',
        'bgblue': '44',
        'bgpurple': '45',
        'bgcyan': '46',
        'bggray': '47',
        'bgwhite': '47',
    }

    reset = template.format(codes['reset'])

    def __call__(self, modifiers, *args, sep=' ', end='', reset=True):
        if isinstance(modifiers, str):
            modifiers = modifiers.split('_')

        codes = self.sep.join(self.codes[mod] for mod in modifiers)
        color_start = self.template.format(codes)

        if reset:
            color_end = self.reset
        else:
            color_end = ''

        text = sprint(*args, sep=sep, end='')
        return f'{color_start}{text}{color_end}{end}'

    def __getattr__(self, name):
        return partial(self, name)

    def print(self, modifiers, *args, sep=' ', end='\n', file=None):
        text = self(modifiers, *args, sep=sep, end=end)
        print(text, end='', file=file)
