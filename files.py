import re
from functools import partial
from pathlib import Path


class Karen:
    """Wants to speak to a context manager.

    >>> file = partial(Karen, open)
    >>> file('ayy.txt', 'w').write('lmao')
    4
    >>> file('ayy.txt', 'r').read()
    'lmao'
    """

    def __init__(self, manager, /, *args, **kwargs):
        self._manager = manager
        self._args = args
        self._kwargs = kwargs

    def __getattr__(self, name):
        def call_method(ctx, *args, **kwargs):
            return getattr(ctx, name)(*args, **kwargs)
        return partial(self, call_method)

    def __call__(self, func, /, *args, **kwargs):
        with self._manager(*self._args, **self._kwargs) as ctx:
            return func(ctx, *args, **kwargs)


file = partial(Karen, open)


class FileTree:
    """A tree backed by a directory of files."""

    disallowed_pattern = re.compile('[^a-z0-9_-]')

    def __init__(self, root, *, sep='.', ext='dat'):
        assert self.disallowed_pattern.search(sep), sep
        assert not self.disallowed_pattern.search(ext), ext
        self.root = root
        self.sep = sep
        self.ext = ext

    def __repr__(self):
        return f"{self.__class__.__name__}({self.root!r})"

    def _disallowed_chars(self, path):
        return self.disallowed_pattern.findall(''.join(path))

    def _validate(self, path):
        assert isinstance(path, tuple), path
        if not path:
            raise Exception("path cannot be empty")
        if not all(path):
            raise Exception("path segments cannot be blank")
        if no := set(self._disallowed_chars(path)):
            s = '' if len(no) == 1 else 's'
            raise Exception(f"path contains disallowed character{s}: {no}")

    def _filename(self, path):
        return self.sep.join(path) + self.sep + self.ext

    def _filepath(self, path):
        self._validate(path)
        filename = self._filename(path)
        return Path(self.root, *path, filename)

    def read(self, *path):
        filepath = self._filepath(path)
        try:
            return filepath.read_bytes()
        except FileNotFoundError as exc:
            raise KeyError(path) from exc

    def write(self, value, *path):
        assert isinstance(value, bytes), value
        filepath = self._filepath(path)
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_bytes(value)

    def delete(self, *path):
        filepath = self._filepath(path)
        try:
            filepath.unlink()
        except FileNotFoundError as exc:
            raise KeyError(path) from exc
        self._prune(filepath.parent)

    def _prune(self, dirpath):
        while dirpath.is_relative_to(self.root):
            try:
                dirpath.rmdir()
            except OSError:
                break
            else:
                dirpath = dirpath.parent

    def contains(self, *path):
        return self._filepath(path).exists()

    def __getitem__(self, key):
        return self.read(*self._key_to_path(key))

    def __setitem__(self, key, value):
        return self.write(value, *self._key_to_path(key))

    def __delitem__(self, key):
        return self.delete(*self._key_to_path(key))

    def __contains__(self, key):
        return self.contains(*self._key_to_path(key))

    def _key_to_path(self, key):
        if isinstance(key, slice):
            raise NotImplementedError(key)
        elif isinstance(key, str):
            return (key,)
        elif not isinstance(key, tuple):
            raise TypeError(key)
        else:
            return key


if __name__ == '__main__':
    stuff = FileTree('stuff')
    root = Path(stuff.root)
    assert not root.exists()

    stuff['foo', 'bar'] = b'ayy lmao'
    stuff['foo'] = b'ayy'
    stuff['bar'] = b'lmao'

    assert root.exists()
    assert stuff['foo'] == b'ayy'
    assert stuff['bar'] == b'lmao'
    assert stuff['foo', 'bar'] == b'ayy lmao'

    del stuff['foo']
    del stuff['bar']
    del stuff['foo', 'bar']

    assert not root.exists()
