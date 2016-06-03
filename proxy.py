from functools import partialmethod


special_method_names = (

    # Basics
    '__repr__',
    '__str__',
    '__bytes__',
    '__format__',

    '__lt__',
    '__le__',
    '__eq__',
    '__ne__',
    '__gt__',
    '__ge__',

    '__hash__',

    '__bool__',

    # Attribute access
    # '__getattr__',
    # '__getattribute__',
    '__setattr__',
    '__delattr__',
    '__dir__',

    # Descriptors
    '__get__',
    '__set__',
    '__delete__',

    # Callable objects
    '__call__',

    # Container types
    '__len__',  # Must return an int
    '__length_hint__',

    '__getitem__',
    '__missing__',
    '__setitem__',
    '__delitem__',
    '__iter__',
    '__reversed__',
    '__contains__',  # `in` casts the return value to bool

    # Numeric types
    '__add__',
    '__sub__',
    '__mul__',
    '__matmul__',
    '__truediv__',
    '__floordiv__',
    '__divmod__',
    '__mod__',
    '__pow__',
    '__lshift__',
    '__rshift__',
    '__and__',
    '__or__',
    '__xor__',

    '__radd__',
    '__rsub__',
    '__rmul__',
    '__rmatmul__',
    '__rtruediv__',
    '__rfloordiv__',
    '__rdivmod__',
    '__rmod__',
    '__rpow__',
    '__rlshift__',
    '__rrshift__',
    '__rand__',
    '__ror__',
    '__rxor__',

    '__neg__',
    '__pos__',
    '__abs__',
    '__invert__',

    # Must return values of the appropriate types
    '__complex__',
    '__int__',
    '__float__',
    '__round__',

    '__index__',  # Must return an int

    '__enter__',
    '__exit__',
    )


inplace_method_names = (
    '__iadd__',
    '__isub__',
    '__imul__',
    '__imatmul__',
    '__itruediv__',
    '__ifloordiv__',
    '__imod__',
    '__ipow__',
    '__ilshift__',
    '__irshift__',
    '__iand__',
    '__ior__',
    '__ixor__',
    )


class Proxy:
    """Channel all object access through a proxy object.

    >>> x = Proxy({'a': 1})
    >>> type(x)
    <class 'proxy.Proxy'>
    >>> x.__class__
    <class 'dict'>
    >>> x.__doc__[:4]
    'dict'
    >>> x
    {'a': 1}
    >>> x == 2
    False
    >>> 2 == x
    False
    >>> str(x)
    "{'a': 1}"
    >>> x.__str__()
    "{'a': 1}"
    >>> x['a'] = 2
    >>> x
    {'a': 2}
    >>> del x['a']
    >>> x['b'] = 3
    >>> x
    {'b': 3}
    >>> x.test = 2
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'test'
    >>> x.delegate
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'delegate'

    TODO: fix these:
    >>> p = Proxy(1)
    >>> p + p
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +: 'Proxy' and 'Proxy'

    If the wrapped object does not define an in-place operation (e.g.,
    immutable types like int and str), the proxy substitutes the
    non-in-place version and updates its wrapped object to the result:

    >>> p = Proxy(1)
    >>> type(p)
    <class 'proxy.Proxy'>
    >>> p.__class__
    <class 'int'>
    >>> p
    1
    >>> p += 1
    >>> type(p)
    <class 'proxy.Proxy'>
    >>> p.__class__
    <class 'int'>
    >>> p
    2

    >>> p = Proxy(set([1]))
    >>> type(p)
    <class 'proxy.Proxy'>
    >>> p -= {1}
    >>> type(p)
    <class 'proxy.Proxy'>
    >>> p.__class__
    <class 'set'>
    >>> p
    set()

    TODO: make the following two tests instead raise:
    TypeError: unsupported operand type(s) for +=: 'set' and 'set'

    >>> p += set([2])
    Traceback (most recent call last):
      ...
    AttributeError: 'set' object has no attribute '__add__'
    >>> p + set([2])
    Traceback (most recent call last):
      ...
    AttributeError: 'set' object has no attribute '__add__'

    # TODO:
    # Special methods in proxied objects are looked up in the usual way,
    # via getattr(type(obj), name):

    # >>> class C:
    # ...     pass
    # ...
    # >>> c = C()
    # >>> c.__len__ = lambda: 5
    # >>> len(c)
    # Traceback (most recent call last):
    #   ...
    # TypeError: object of type 'C' has no len()
    # >>> p = Proxy(c)
    # >>> len(p)
    # Traceback (most recent call last):
    #   ...
    # TypeError: object of type 'C' has no len()
    """

    def __init__(self, obj):
        super().__setattr__('__wrapped__', obj)

    def __getattribute__(self, name):
        wrapped = super().__getattribute__('__wrapped__')
        wrapper = super().__getattribute__('wrapper')
        return wrapper(wrapped, name)

    def wrapper(self, wrapped, name):
        return getattr(wrapped, name)

    # Certain implicit invocations of special methods may bypass
    # __getattribute__: for example, `len(Proxy([]))` invokes
    # Proxy.__len__ directly.

    # Solution: make sure all accesses are properly forwarded by
    # defining each special method on the Proxy class and invoking
    # Proxy.__getattribute__ from within.

    def delegate(self, name, *args, **kwargs):
        # I literally have no idea how this works anymore.
        return getattr(self, name)(*args, **kwargs)

    for name in special_method_names:
        locals()[name] = partialmethod(delegate, name)
        # Clean up temporary variable
        # (NameError if done outside an empty loop)
        del name

    def inplace_delegate(self, name, *args, **kwargs):
        """Delegate the named in-place method to the wrapped object.

        If the wrapped object does not define an in-place version of the
        method, fall back to the regular version and return a new Proxy
        object wrapping the result, mimicking the behavior of ints and
        other immutable objects.

        >>> p = Proxy([])
        >>> q = p
        >>> p += [1]
        >>> p
        [1]
        >>> q
        [1]
        >>> p is q
        True

        >>> p = Proxy(1)
        >>> q = p
        >>> p += 1
        >>> p
        2
        >>> q
        1
        >>> p is q
        False
        """
        try:
            attr = getattr(self, name)
        except AttributeError:
            # If the in-place version was not found, fall back to the
            # regular version and return a new Proxy object.
            attr = getattr(self, name.replace('i', '', 1))  # ZOMG HAX
            new_obj = attr(*args, **kwargs)
            return type(self)(new_obj)
        else:
            # Otherwise, update this Proxy object's wrapped value.
            # (Most objects will probably just return `self` from the
            # in-place operation, but that is not a guarantee.)
            new_obj = attr(*args, **kwargs)
            super().__setattr__('__wrapped__', new_obj)
            return self

    for name in inplace_method_names:
        locals()[name] = partialmethod(inplace_delegate, name)
        del name


class PrintingProxy(Proxy):
    """Test and demonstration class.

    >>> x = PrintingProxy({'a': 1})
    >>> type(x)
    <class 'proxy.PrintingProxy'>
    >>> x.__class__
    looking for __class__
    <class 'dict'>
    >>> x.__doc__[:4]
    looking for __doc__
    'dict'
    >>> x
    looking for __repr__
    {'a': 1}
    >>> x == 2
    looking for __eq__
    False
    >>> 2 == x
    looking for __eq__
    False
    >>> x.__str__()
    looking for __str__
    "{'a': 1}"
    >>> str(x)
    looking for __str__
    "{'a': 1}"
    >>> x['a'] = 2
    looking for __setitem__
    >>> x
    looking for __repr__
    {'a': 2}
    >>> del x['a']
    looking for __delitem__
    >>> x['b'] = 3
    looking for __setitem__
    >>> x
    looking for __repr__
    {'b': 3}
    >>> x.test = 2
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'test'
    >>> x.delegate
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'delegate'


    >>> len(PrintingProxy([]))
    looking for __len__
    0

    >>> p1 = PrintingProxy(1)
    >>> p1
    looking for __repr__
    1
    >>> p1 + 1
    looking for __add__
    2
    >>> 1 + p1
    looking for __radd__
    2
    >>> sum([p1, 1])
    looking for __radd__
    2
    >>> sum([1, p1])
    looking for __radd__
    2
    """

    def wrapper(self, wrapped, name):
        print('looking for', name)
        return getattr(wrapped, name)


class CallbackProxy:
    """Invoke a callback every time the proxy's value is accessed.

    TODO: replace regular Proxy

    LOL WUT:
    >>> x = CallbackProxy(iter(range(10)).__next__)
    >>> x
    0
    >>> x
    1
    >>> x
    2
    """

    def __init__(self, callback):
        super().__setattr__('callback', callback)

    def __getattribute__(self, name):
        obj = super().__getattribute__('callback')()
        return getattr(obj, name)

    # Certain implicit invocations of special methods may bypass
    # __getattribute__: for example, `len(Proxy([]))` invokes
    # Proxy.__len__ directly.

    # Solution: make sure all accesses are properly forwarded by
    # defining each special method on the Proxy class and invoking
    # Proxy.__getattribute__ from within.

    def delegate(self, name, *args, **kwargs):
        # I literally have no idea how this works anymore.
        return getattr(self, name)(*args, **kwargs)

    for name in special_method_names + inplace_method_names:
        locals()[name] = partialmethod(delegate, name)
        # Clean up temporary variable
        # (NameError if done outside an empty loop)
        del name
