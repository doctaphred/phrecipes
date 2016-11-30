from caching import cache
from copy import deepcopy
from functools import wraps
from getpass import getpass as _getpass
from magic import magic


@cache
def secretcls(cls):

    def __repr__(self):
        return '<{}#{}>'.format(
            self.__class__.__name__, id(self))

    return type('Secret[{}]'.format(cls.__name__), (cls,),
                {'__repr__': __repr__})


@magic
class secret:

    def __getitem__(self, key):
        return secretcls(key)

    def __call__(self, value):
        secretcls = self[type(value)]
        try:
            cp = deepcopy(value)
            cp.__class__ = secretcls
            return cp
        except TypeError:
            return secretcls(value)


@wraps(_getpass)
def getpass(*args, **kwargs):
    """
    >>> x = getpass()
    Password:
    >>> x
    <Secret[str]#4332858128>
    >>> print(x)
    hunter2
    """
    return secret(_getpass(*args, **kwargs))
