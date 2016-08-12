import sys
from types import ModuleType


def modulify(cls):
    """Replace the class' module with an instance of the class.

    Useful for creating modules with __getattr__, descriptors, etc.
    """
    dct = dict(vars(cls))
    # Make sure __init__ is defined, to avoid falling back to
    # ModuleType.__init__ (which requires an argument)
    dct.setdefault('__init__', object.__init__)
    mod = type(cls.__name__, (ModuleType,), dct)
    sys.modules[cls.__module__] = mod()
