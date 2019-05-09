Extended doctests for ``funccools``
===================================

..
    >>> from funccools import *

``curried``
-----------

This decorator must see through the lies of its wrapped function.

    >>> @curried
    ... def deception():
    ...     raise TypeError(
    ...         "deception() missing 1 required positional argument: 'ayy'"
    ...     )

    >>> deception()
    Traceback (most recent call last):
      ...
    TypeError: deception() missing 1 required positional argument: 'ayy'

    >>> deception('ayy')
    Traceback (most recent call last):
      ...
    TypeError: deception() takes 0 positional arguments but 1 was given

    >>> deception(ayy='lmao')
    Traceback (most recent call last):
      ...
    TypeError: deception() got an unexpected keyword argument 'ayy'
