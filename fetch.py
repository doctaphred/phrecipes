from pathlib import Path
import importlib.util


def fetch(path, name=None):
    """Load a module from an arbitrary path."""
    path = Path(path)
    if name is None:
        name = path.stem
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
