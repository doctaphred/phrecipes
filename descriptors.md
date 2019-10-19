Extended doctests for `descriptors`
===================================

    >>> from descriptors import *

    >>> from itertools import count

    >>> def info(obj):
    ...     "Print the object's type and public attributes."
    ...     print(type(obj).__name__)
    ...     for attr in dir(obj):
    ...         if not attr.startswith('_'):
    ...             print('  -', attr)

    >>> class Class:
    ...     @lazyattr
    ...     def number(self, *, numbers=count(1)):
    ...         n = next(numbers)
    ...         print(self, '->', n)
    ...         return n

    >>> info(Class)
    type
      - number

    >>> Class.number
    <descriptors.lazyattr object at ...>

    >>> Class.number()
    Traceback (most recent call last):
        ...
    TypeError: 'lazyattr' object is not callable


The lazyattr appears in the instance's `dir()` even before it has been
evaluated.

    >>> obj = Class()

    >>> vars(obj)
    {}
    >>> info(obj)
    Class
      - number


When the attribute is first accessed, the wrapped method is called, and
the returned value is set on the instance.

    >>> obj.number
    <__main__.Class object at ...> -> 1
    1

    >>> vars(obj)
    {'number': 1}
    >>> info(obj)
    Class
      - number


Since the lazyattr is a non-data descriptor, subsequent accesses of the
same attribute simply return the instance attribute, and the method is
not called again, unless the instance attribute is deleted.

    >>> obj.number
    1

    >>> vars(obj)
    {'number': 1}
    >>> info(obj)
    Class
      - number

    >>> del obj.number

    >>> vars(obj)
    {}
    >>> info(obj)
    Class
      - number

    >>> obj.number
    <__main__.Class object at ...> -> 2
    2

    >>> vars(obj)
    {'number': 2}
    >>> info(obj)
    Class
      - number


lazyattrs can be patched like normal attributes.

    >>> obj.number = 'ayy'
    >>> vars(obj)
    {'number': 'ayy'}

    >>> del obj.number
    >>> vars(obj)
    {}

    >>> obj.number
    <__main__.Class object at ...> -> 3
    3
    >>> vars(obj)
    {'number': 3}


TODO: handle aliases better:

    >>> Class.alias = Class.number

    >>> info(Class)
    type
      - alias
      - number

    >>> vars(obj)
    {'number': 3}
    >>> info(obj)
    Class
      - alias
      - number

    >>> obj.alias
    <__main__.Class object at ...> -> 4
    4

    >>> vars(obj)
    {'number': 4}
    >>> info(obj)
    Class
      - alias
      - number


Comparison with property:


    >>> class Class:
    ...     @property
    ...     def number(self, *, numbers=count(1)):
    ...         n = next(numbers)
    ...         print(self, '->', n)
    ...         return n

    >>> Class.number
    <property object at ...>

    >>> Class.number()
    Traceback (most recent call last):
        ...
    TypeError: 'property' object is not callable

    >>> obj = Class()

    >>> info(obj)
    Class
      - number

    >>> obj.number
    <__main__.Class object at ...> -> 1
    1
    >>> obj.number
    <__main__.Class object at ...> -> 2
    2


Comparison with regular method:

    >>> class Class:
    ...     def number(self, *, numbers=count(1)):
    ...         n = next(numbers)
    ...         print(self, '->', n)
    ...         return n

    >>> Class.number
    <function Class.number at ...>

    >>> Class.number()
    Traceback (most recent call last):
        ...
    TypeError: number() missing 1 required positional argument: 'self'

    >>> obj = Class()

    >>> info(obj)
    Class
      - number

    >>> obj.number
    <bound method Class.number of <__main__.Class object at ...>>

    >>> obj.number()
    <__main__.Class object at ...> -> 1
    1
    >>> obj.number()
    <__main__.Class object at ...> -> 2
    2
