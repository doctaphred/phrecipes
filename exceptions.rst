Extended doctests for ``exceptions``
====================================

..
    >>> from exceptions import *

``raises``
----------

Allowed exceptions must inherit from the given base exception.

    >>> raises(BaseException)
    Traceback (most recent call last):
      ...
    ValueError: allowed exceptions must inherit from the given base class (Exception); BaseException does not

    >>> raises(Exception)
    Traceback (most recent call last):
      ...
    ValueError: allowed exceptions must inherit from the given base class (Exception); Exception does not

Exceptions which do not inherit from base are allowed to raise normally.

    >>> @raises(ConnectionError, base=OSError)
    ... def f(exc):
    ...     raise exc

    >>> f(BrokenPipeError)  # Subclass of ConnectionError
    Traceback (most recent call last):
      ...
    BrokenPipeError

    >>> f(BlockingIOError)  # Subclass of OSError
    Traceback (most recent call last):
      ...
    exceptions.UnexpectedException: BlockingIOError

    >>> f(ValueError)  # Not a subclass of OSError
    Traceback (most recent call last):
      ...
    ValueError

You can allow Exceptions, but don't do that.

    >>> @raises(Exception, base=BaseException)
    ... def y_tho(exc):
    ...     raise exc

    >>> y_tho(Exception)
    Traceback (most recent call last):
      ...
    Exception

    >>> y_tho(KeyboardInterrupt)
    Traceback (most recent call last):
      ...
    exceptions.UnexpectedException: KeyboardInterrupt

    >>> y_tho(SystemExit)
    Traceback (most recent call last):
      ...
    exceptions.UnexpectedException: SystemExit

    >>> y_tho(BaseException)
    Traceback (most recent call last):
      ...
    exceptions.UnexpectedException: BaseException
