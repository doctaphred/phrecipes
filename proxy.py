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

binary_method_names = (
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
    """Transparently wrap an object with another object.

    --------------------------------------------------------------------

    Proxies behave just like the objects they wrap:

    >>> x = Proxy({})

    >>> x
    {}

    >>> x['a'] = 1
    >>> x
    {'a': 1}

    >>> x.__str__()
    "{'a': 1}"

    >>> str(x)
    "{'a': 1}"

    >>> x['a'] = 2
    >>> x
    {'a': 2}

    >>> del x['a']; x['b'] = 3; x
    {'b': 3}

    --------------------------------------------------------------------

    Only the `type` function gives the Proxy away:

    >>> Proxy({}).__class__
    <class 'dict'>

    >>> x.__doc__[:4]
    'dict'

    >>> type(Proxy({}))
    <class 'proxy.Proxy'>

    --------------------------------------------------------------------

    Attribute assignment occurs on the wrapped object:

    >>> f = lambda: None
    >>> g = f
    >>> g.attr = 2
    >>> g.attr
    2
    >>> f.attr
    2

    >>> f = lambda: None
    >>> p = Proxy(f)
    >>> p.attr = 2
    >>> p.attr
    2
    >>> f.attr
    2
    >>> f == p
    True

    >>> {}.attr = 2
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'attr'

    >>> Proxy({}).attr = 2
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'attr'

    --------------------------------------------------------------------

    The Proxy class' own attributes are not directly accessible:

    >>> Proxy({}).delegate_special
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'delegate_special'

    >>> Proxy({}).delegate_inplace
    Traceback (most recent call last):
      ...
    AttributeError: 'dict' object has no attribute 'delegate_inplace'

    >>> type(Proxy({})).delegate_special  # doctest: +ELLIPSIS
    <function Proxy.delegate_special at ...>

    >>> object.__getattribute__(Proxy({}), 'delegate_special')
    <bound method Proxy.delegate_special of {}>

    >>> object.__getattribute__(Proxy({}), 'ayyy_lmao')
    Traceback (most recent call last):
      ...
    AttributeError: 'Proxy' object has no attribute 'ayyy_lmao'

    --------------------------------------------------------------------

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

    >>> p = Proxy({1})
    >>> type(p)
    <class 'proxy.Proxy'>
    >>> p -= {1}
    >>> type(p)
    <class 'proxy.Proxy'>
    >>> p.__class__
    <class 'set'>
    >>> p
    set()

    --------------------------------------------------------------------

    Some exception messages may be altered, but the exception types
    remain the same:

    >>> set() + set()
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +: 'set' and 'set'

    >>> Proxy(set()) + set()
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +: 'Proxy' and 'set'

    >>> set() + Proxy(set)
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +: 'set' and 'Proxy'

    >>> s = set()
    >>> s += set()
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +=: 'set' and 'set'

    >>> s += Proxy(set)
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +=: 'set' and 'Proxy'

    >>> p = Proxy(set())
    >>> p += set()
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +=: 'Proxy' and 'set'

    >>> p += Proxy(set)
    Traceback (most recent call last):
      ...
    TypeError: unsupported operand type(s) for +=: 'Proxy' and 'Proxy'

    --------------------------------------------------------------------

    Special methods are looked up via `getattr(obj.__class__, name)`,
    matching the behavior of the interpreter:

    >>> class C: pass
    >>> c = C()
    >>> c.__len__ = lambda: 5
    >>> c.__len__()
    5
    >>> len(c)
    Traceback (most recent call last):
      ...
    TypeError: object of type 'C' has no len()

    >>> p = Proxy(c)
    >>> p.__len__()
    5
    >>> len(p)
    Traceback (most recent call last):
      ...
    TypeError: type object 'C' has no attribute '__len__'

    >>> f = lambda: None
    >>> f.__eq__ = lambda self, other: True
    >>> f == 2
    False
    """

    def __init__(self, obj):
        super().__setattr__('wrapped_obj', obj)

    def __getattribute__(self, name):
        wrapped_obj = super().__getattribute__('wrapped_obj')
        getattr_wrapper = super().__getattribute__('getattr_wrapper')
        return getattr_wrapper(wrapped_obj, name)

    def getattr_wrapper(self, wrapped_obj, name):
        """Override this method in subclasses to alter the proxy's behavior."""
        return getattr(wrapped_obj, name)

    # Certain implicit invocations of special methods may bypass
    # __getattribute__: for example, `len(Proxy([]))` invokes
    # Proxy.__len__ directly.

    # Solution: make sure all accesses are properly forwarded by
    # defining each special method on the Proxy class and invoking
    # Proxy.__getattribute__ from within.

    def delegate_special(self, name, *args, **kwargs):
        """Delegate the named special method to the wrapped object.

        ----------------------------------------------------------------

        Binary special methods are looked up on the class of the object,
        rather than the object itself:

        >>> f = lambda: None
        >>> f.__len__ = lambda: print('calling __len__')
        >>> f.__len__()
        calling __len__
        >>> len(f)
        Traceback (most recent call last):
          ...
        TypeError: object of type 'function' has no len()

        >>> p = Proxy(lambda: None)
        >>> p.__len__ = lambda: print('calling __len__')
        >>> p.__len__()
        calling __len__
        >>> len(p)
        Traceback (most recent call last):
          ...
        TypeError: type object 'function' has no attribute '__len__'

        """
        wrapped_obj = super().__getattribute__('wrapped_obj')
        getattr_wrapper = super().__getattribute__('getattr_wrapper')
        try:
            wrapped_method = getattr_wrapper(wrapped_obj.__class__, name)
        except AttributeError as e:
            raise TypeError(e)
        else:
            return wrapped_method(wrapped_obj, *args, **kwargs)

    for name in special_method_names:
        locals()[name] = partialmethod(delegate_special, name)
        # Clean up temporary variable
        # (NameError if done outside an empty loop)
        del name

    def delegate_binary(self, name, *args, **kwargs):
        """Delegate the named binary method, or return NotImplemented.

        >>> p = Proxy([1])
        >>> Proxy.delegate_binary(p, '__add__', [2])
        [1, 2]
        >>> Proxy.delegate_binary(p, '__sub__', [2])
        NotImplemented

        ----------------------------------------------------------------

        Binary special methods are looked up on the class of the object,
        rather than the object itself:

        >>> f = lambda: None
        >>> f.__add__ = lambda value: print('adding', value)
        >>> f.__add__(1)
        adding 1
        >>> f + 1
        Traceback (most recent call last):
          ...
        TypeError: unsupported operand type(s) for +: 'function' and 'int'

        >>> p = Proxy(lambda: None)
        >>> p.__add__ = lambda value: print('adding', value)
        >>> p.__add__(1)
        adding 1
        >>> p + 1
        Traceback (most recent call last):
          ...
        TypeError: unsupported operand type(s) for +: 'Proxy' and 'int'
        """
        wrapped_obj = super().__getattribute__('wrapped_obj')
        getattr_wrapper = super().__getattribute__('getattr_wrapper')
        try:
            wrapped_method = getattr_wrapper(wrapped_obj.__class__, name)
        except AttributeError:
            return NotImplemented
        else:
            return wrapped_method(wrapped_obj, *args, **kwargs)

    for name in binary_method_names:
        locals()[name] = partialmethod(delegate_binary, name)
        del name

    def delegate_inplace(self, name, *args, **kwargs):
        """Delegate the named in-place method, or return NotImplemented.

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

        ----------------------------------------------------------------

        In-place special methods are looked up on the class of the
        object, rather than the object itself:

        >>> f = lambda: None
        >>> f.__iadd__ = lambda value: print('inplace-adding', value)
        >>> f.__iadd__(1)
        inplace-adding 1
        >>> f += 1
        Traceback (most recent call last):
          ...
        TypeError: unsupported operand type(s) for +=: 'function' and 'int'

        >>> p = Proxy(lambda: None)
        >>> p.__iadd__ = lambda value: print('inplace-adding', value)
        >>> p.__iadd__(1)
        inplace-adding 1
        >>> p += 1
        Traceback (most recent call last):
          ...
        TypeError: unsupported operand type(s) for +=: 'Proxy' and 'int'

        ----------------------------------------------------------------

        Note that the in-place methods may return a value, even though
        they may not be used as an expression unless invoked directly:

        >>> x = [1].__iadd__([2])
        >>> x
        [1, 2]
        >>> x = ([1] += [2])
        Traceback (most recent call last):
          ...
            x = ([1] += [2])
                      ^
        SyntaxError: invalid syntax


        >>> p = Proxy([1])
        >>> x = Proxy.delegate_inplace(p, '__iadd__', [2])
        >>> x
        [1, 2]
        >>> p
        [1, 2]
        >>> x = (p += [2])
        Traceback (most recent call last):
          ...
            x = (p += [2])
                    ^
        SyntaxError: invalid syntax

        """
        wrapped_obj = super().__getattribute__('wrapped_obj')
        getattr_wrapper = super().__getattribute__('getattr_wrapper')
        try:
            wrapped_method = getattr_wrapper(wrapped_obj.__class__, name)
        except AttributeError:
            # If the in-place version was not found, fall back to the
            # regular version and return a new Proxy object.
            try:
                fallback_name = name.replace('i', '', 1)  # ZOMG HAX
                wrapped_fallback_method = getattr_wrapper(
                    wrapped_obj.__class__, fallback_name)
            except AttributeError:
                # If the regular version was not found, return
                # NotImplemented and let the interpreter sort it out.
                return NotImplemented
            else:
                new_obj = wrapped_fallback_method(wrapped_obj, *args, **kwargs)
                return type(self)(new_obj)
        else:
            # Otherwise, update this Proxy object's wrapped value.
            # (Most objects will probably just return `self` from the
            # in-place operation, but that is not a guarantee.)
            new_obj = wrapped_method(wrapped_obj, *args, **kwargs)
            super().__setattr__('wrapped_obj', new_obj)
            return self

    for name in inplace_method_names:
        locals()[name] = partialmethod(delegate_inplace, name)
        del name


class PrintingProxy(Proxy):
    """Test and demonstration class.

    --------------------------------------------------------------------

    >>> x = PrintingProxy({'a': 1})

    >>> type(x)
    <class 'proxy.PrintingProxy'>

    >>> x.__class__
    looking for __class__ on {'a': 1}
    <class 'dict'>

    >>> x.__doc__[:4]
    looking for __doc__ on {'a': 1}
    'dict'

    >>> x
    looking for __repr__ on <class 'dict'>
    {'a': 1}
    >>> x == 2
    looking for __eq__ on <class 'dict'>
    False
    >>> 2 == x
    looking for __eq__ on <class 'dict'>
    False

    >>> str(x)
    looking for __str__ on <class 'dict'>
    "{'a': 1}"

    >>> x.__str__()
    looking for __str__ on {'a': 1}
    "{'a': 1}"

    --------------------------------------------------------------------

    >>> x['a'] = 2
    looking for __setitem__ on <class 'dict'>
    >>> x
    looking for __repr__ on <class 'dict'>
    {'a': 2}
    >>> del x['a']
    looking for __delitem__ on <class 'dict'>
    >>> x['b'] = 3
    looking for __setitem__ on <class 'dict'>
    >>> x
    looking for __repr__ on <class 'dict'>
    {'b': 3}

    >>> len(PrintingProxy([]))
    looking for __len__ on <class 'list'>
    0

    >>> p1 = PrintingProxy(1)
    >>> p1
    looking for __repr__ on <class 'int'>
    1
    >>> p1 + 1
    looking for __add__ on <class 'int'>
    2
    >>> 1 + p1
    looking for __radd__ on <class 'int'>
    2
    >>> sum([p1, 1])
    looking for __radd__ on <class 'int'>
    2
    >>> sum([1, p1])
    looking for __radd__ on <class 'int'>
    2
    """

    def getattr_wrapper(self, wrapped_obj, name):
        print('looking for', name, 'on', wrapped_obj)
        return getattr(wrapped_obj, name)


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
        callback_result = super().__getattribute__('callback')()
        return getattr(callback_result, name)

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
