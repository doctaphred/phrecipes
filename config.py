import sys
from pathlib import Path


def get_main_dir():
    main = sys.modules['__main__']
    try:
        main_path = main.__file__
    except AttributeError:
        return Path.cwd()
    else:
        return Path(main_path).resolve().parent

