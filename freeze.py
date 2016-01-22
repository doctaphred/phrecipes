from collections.abc import Iterable, Mapping, Set


def frozen(struct):
    """Return an immutable, hashable version of the given data structure.

    Iterators (including generators) are hashable but mutable, so they
    are evaluated and returned as tuples---if they are infinite, this
    function will not exit.
    """
    if isinstance(struct, Mapping):
        return frozenset((k, frozen(v)) for k, v in struct.items())
    if isinstance(struct, Set):
        return frozenset(frozen(item) for item in struct)
    if isinstance(struct, Iterable):  # Includes iterators and generators
        return tuple(frozen(item) for item in struct)
    hash(struct)  # Raise TypeError for unhashable objects
    return struct


def hashified(struct, use_none=False):
    """Return a hashable version of the given data structure.

    If use_none is True, returns None instead of raising TypeError for
    unhashable types: this will serve as a bad but sometimes passable
    hash.
    """
    try:
        hash(struct)
    except TypeError:
        pass
    else:
        # Return the original object if it's already hashable
        return struct

    if isinstance(struct, Mapping):
        return frozenset((k, hashified(v)) for k, v in struct.items())
    if isinstance(struct, Set):
        return frozenset(hashified(item) for item in struct)
    if isinstance(struct, Iterable):
        return tuple(hashified(item) for item in struct)

    if use_none:
        return None

    raise TypeError('unhashable type: {.__name__!r}'.format(type(struct)))
