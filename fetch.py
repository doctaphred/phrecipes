import importlib.util
import sys
from pathlib import Path
from types import ModuleType
from urllib.parse import urlparse

import requests


def fetch(path, name=None):
    """Load a module from an arbitrary path."""
    path = Path(path)
    if name is None:
        name = path.stem
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def import_from_url(url, name=None):
    """lol dont do this"""
    code = requests.get(url).text
    if name is None:
        name = Path(urlparse(url).path).stem
    sys.modules[name] = module = ModuleType(name)
    module.__loader__ = None
    # Non-package modules should not have a __path__ attribute.
    # When the module is not a package, __package__ should be set to the
    # empty string for top-level modules
    module.__package__ = ''
    exec(code, module.__dict__)
    return module
