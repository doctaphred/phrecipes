"""A somewhat nicer way to work with `os.environ`."""
import os


def getenv(name, convert=str, default=None):
    """
    >>> os.environ['JSON_CONFIG'] = '{"ayy": "lmao"}'
    >>> getenv('JSON_CONFIG')
    '{"ayy": "lmao"}'

    >>> import json
    >>> getenv('JSON_CONFIG', convert=json.loads)
    {'ayy': 'lmao'}

    >>> getenv('NOPE', convert=json.loads)
    >>> getenv('NOPE', convert=json.loads, default={})
    {}

    >>> import ast
    >>> getenv('JSON_CONFIG', convert=ast.literal_eval)
    {'ayy': 'lmao'}
    """
    from os import environ
    return convert(environ[name]) if name in environ else default


def env_config(prefix, spec, get=os.environ.get):
    """Create a config dict from the environment.

    >>> spec = [
    ...     ('flag1', bool, ''),
    ...     ('flag2', bool, '1'),
    ...     ('number', int, '3'),
    ...     ('list', str.split, ''),
    ... ]

    >>> env_config('REALLY_LONG_PREFIX_', spec)
    {'flag1': False, 'flag2': True, 'number': 3, 'list': []}

    >>> alternate_env = {
    ...     'REALLY_LONG_PREFIX_FLAG1': '1',
    ...     'REALLY_LONG_PREFIX_FLAG2': '',
    ...     'REALLY_LONG_PREFIX_LIST': 'a b c',
    ... }

    >>> env_config('REALLY_LONG_PREFIX_', spec, get=alternate_env.get)
    {'flag1': True, 'flag2': False, 'number': 3, 'list': ['a', 'b', 'c']}

    """
    return {
        name: convert(get(prefix + name.upper(), default))
        for name, convert, default in spec
    }


class Env:
    """Access os.environ with getattr syntax and type conversions.

    >>> os.environ['MYAPP_JSON_CONFIG'] = '{"ayy": "lmao"}'
    >>> os.environ['MYAPP_PYTHON_OBJECT'] = "{(b'',): [(1+0j)]}"

    >>> import ast, json
    >>> env = Env({
    ...         'json_config': (json.loads, {}),
    ...         'python_object': (ast.literal_eval, object()),
    ...         'the_answer': (int, 42),
    ...     },
    ...     prefix='MYAPP_',
    ... )

    >>> env.json_config
    {'ayy': 'lmao'}

    >>> env.python_object
    {(b'',): [(1+0j)]}

    >>> env.the_answer
    42

    >>> os.environ['MYAPP_THE_ANSWER'] = '420'
    >>> env.the_answer
    420

    >>> del os.environ['MYAPP_PYTHON_OBJECT']
    >>> env.python_object  # doctest: +ELLIPSIS
    <object object at ...>

    >>> env.nope  # doctest: +ELLIPSIS
    Traceback (most recent call last):
      ...
    AttributeError: 'nope'. Choices are: ['json_config', ...]

    >>> from pprint import pprint
    >>> pprint(dict(env))  # doctest: +ELLIPSIS
    {'json_config': {'ayy': 'lmao'},
     'python_object': <object object at ...>,
     'the_answer': 420}
    """
    __slots__ = ('_prefix', '_expected', '_environ')

    def __init__(self, expected, prefix='', environ=os.environ):
        """
        Parameters
        ----------
        expected: {<name>: (<convert>, <default>)}
            name: str
                Name of the environment variable.
            convert: function
                Function to convert the raw string value into a Python
                value. Use `str` if no conversion is needed, or
                `ast.literal_eval` to parse the value as a Python
                literal of arbitrary type.
            default: object
                Value to return if <name> is not set in the environment.

        prefix: str
            Prefix to apply to all variable names.

        environ: dict
            Backing dictionary.
        """
        self._prefix = prefix
        self._expected = expected
        self._environ = environ
        assert isinstance(self._expected, dict)
        assert all(len(x) == 2 for x in self._expected.values())

    def _env_name(self, name):
        return self._prefix + name.upper()

    def __getattr__(self, name):
        try:
            convert, default = self._expected[name]
        except KeyError as exc:
            msg = f"{name!r}. Choices are: {dir(self)}"
            raise AttributeError(msg) from exc

        env_name = self._env_name(name)
        if env_name in self._environ:
            return convert(self._environ[env_name])
        else:
            return default

    def __iter__(self):
        for name in self._expected:
            yield name, getattr(self, name)

    def __dir__(self):
        return self._expected
