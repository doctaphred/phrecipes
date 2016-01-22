import time
from functools import lru_cache, update_wrapper
from importlib import import_module, reload


class ReloadingModule:
    """Wrapper for a module, reloading it on every attribute access."""

    def __init__(self, module, lifespan=0.1):
        """
        Args:
            module: the module to reload on attribute access.
            lifespan: how long to wait between reloads, in seconds.
        """
        update_wrapper(self, module)
        self._module = module
        self._last_reloaded = time.time()
        self.lifespan = lifespan

    def __dir__(self):
        return dir(self._module)

    def __getattr__(self, name):
        if time.time() - self._last_reloaded > self.lifespan:
            self._module = reload(self._module)
            self._last_reloaded = time.time()
        return getattr(self._module, name)


@lru_cache()
def live(name, *args, package=None, **kwargs):
    """Return a live-reloading wrapper for the given module.

    A common use is to allow altering configuration options while a
    program is running.

    Note that this function uses importlib.reload, which alters the
    state not only of the returned object, but of the corresponding
    module in sys.modules as well.

    Args:
        name, package: passed to importlib.import_module.
        *args, **kwargs: passed to ReloadingModule.__init__.
    """
    module = import_module(name, package)
    return ReloadingModule(module, *args, **kwargs)
