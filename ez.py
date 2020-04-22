from types import FunctionType, MethodType


def ezrepr(obj):
    """Create a repr of <obj> based on its instance attributes and type.

    >>> def func(): pass
    >>> print(ezrepr(func))
    func

    >>> class Class: pass
    >>> print(ezrepr(Class))
    Class

    >>> obj = Class()
    >>> print(ezrepr(obj))
    Class()

    >>> obj.ayy = 'lmao'
    >>> obj._private = 'nope'
    >>> print(ezrepr(obj))
    Class(ayy='lmao')

    >>> class Outer:
    ...     class Inner:
    ...         def method(self): pass
    ...     def method(self): pass

    >>> print(ezrepr(Outer))
    Outer
    >>> print(ezrepr(Outer.Inner))
    Outer.Inner
    >>> print(ezrepr(Outer()))
    Outer()
    >>> print(ezrepr(Outer.Inner()))
    Outer.Inner()

    >>> print(ezrepr(Outer.method))
    Outer.method
    >>> print(ezrepr(Outer.Inner.method))
    Outer.Inner.method

    >>> print(ezrepr(Outer().method))
    Outer().method
    >>> print(ezrepr(Outer.Inner().method))
    Outer.Inner().method

    >>> class Slotted:
    ...     __slots__ = ['ayy', 'lmao']
    ...     __init__ = ezinit
    ...
    >>> print(ezrepr(Slotted))
    Slotted
    >>> print(ezrepr(Slotted()))
    Slotted()
    >>> print(ezrepr(Slotted(ayy='lmao')))
    Slotted(ayy='lmao')
    """
    if isinstance(obj, (type, FunctionType)):
        return obj.__qualname__
    if isinstance(obj, MethodType):
        return f"{ezrepr(obj.__self__)}.{obj.__name__}"

    if hasattr(obj, '__dict__'):
        sig = ', '.join(
            f'{attr}={value!r}'
            for attr, value in vars(obj).items()
            if not attr.startswith('_')
        )
        return f"{type(obj).__qualname__}({sig})"

    if hasattr(obj, '__slots__'):
        sig = ', '.join(
            f'{attr}={getattr(obj, attr)!r}'
            for attr in obj.__slots__
            if not attr.startswith('_')
            and hasattr(obj, attr)
        )
        return f"{type(obj).__qualname__}({sig})"

    return repr(obj)


def ezinit(obj, **attrs):
    """Assign <attrs> to <obj>, but only if they're defined on its type.

    Best used as a class' __init__ method.
    """
    names = {
        name for name in dir(type(obj))
        if not name.startswith('__')
        and not name.endswith('__')
    }
    unexpected = attrs.keys() - names
    if unexpected:
        raise TypeError(f'unexpected attrs: {unexpected}')
    for attr, value in attrs.items():
        setattr(obj, attr, value)


def ezclone(obj, **attrs):
    """Return a clone of <obj>, but with some updated attrs.

    Best used as the __call__ method of an ezinit class.
    """
    return type(obj)(**{**vars(obj), **attrs})


class ez:
    """
    >>> class cls(ez):
    ...     ayy = 'ayy'

    >>> obj = cls()
    >>> obj
    cls()
    >>> obj.ayy
    'ayy'

    >>> cls(ayy='lmao')
    cls(ayy='lmao')

    >>> obj2 = obj(ayy='lmao')
    >>> obj2.ayy
    'lmao'
    >>> obj2
    cls(ayy='lmao')

    >>> cls(nope='lmao')
    Traceback (most recent call last):
      ...
    TypeError: unexpected attrs: {'nope'}
    """
    __init__ = ezinit
    __call__ = ezclone
    __repr__ = ezrepr
