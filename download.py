from contextlib import contextmanager
import hashlib
import io

import requests

from retry import call_with_retries


@contextmanager
def reset_buffer(buffer: io.IOBase):
    start_position = buffer.tell()
    try:
        yield
    except Exception:
        buffer.seek(start_position)
        buffer.truncate()
        raise
    else:
        buffer.seek(start_position)


class ChecksumMismatch(Exception):
    """
    >>> ChecksumMismatch.verify(None, None)
    >>> ChecksumMismatch.verify('ayy', 'lmao')
    Traceback (most recent call last):
      ...
    download.ChecksumMismatch: expected 'ayy', got 'lmao'
    """

    def __init__(self, expected, actual):
        super().__init__()
        self.expected = expected
        self.actual = actual

    def __str__(self):
        return f"expected {self.expected!r}, got {self.actual!r}"

    @classmethod
    def verify(cls, expected, actual):
        if expected != actual:
            raise cls(expected, actual)


def download(checksum, url, to, *, chunk_size=128, hasher=hashlib.sha256):
    hasher = hasher()
    if isinstance(checksum, bytes):
        digest = hasher.digest
    elif isinstance(checksum, str):
        digest = hasher.hexdigest
    else:
        raise TypeError(
            f"expected bytes or str, got {type(checksum)} ({checksum!r})"
        )

    response = requests.get(url, stream=True)

    with reset_buffer(to):
        for chunk in response.iter_content(chunk_size=chunk_size):
            to.write(chunk)
            hasher.update(chunk)
        ChecksumMismatch.verify(checksum, digest())


if __name__ == '__main__':
    import logging

    logging.basicConfig(
        format=' '.join([
            '[%(asctime)s]',
            '%(levelname)s',
            '%(pathname)s:%(lineno)d',
            '(%(funcName)s)',
            '%(message)s',
        ]),
        datefmt='%Y-%m-%dT%H:%M:%S',
        level='DEBUG',
    )

    checksum = '990367719d27691ef653206ca030a1efa9d19423275c6b2622f0ab4813747063'  # noqa
    url = 'https://raw.githubusercontent.com/doctaphred/emojencode/master/LICENSE'  # noqa

    with io.BytesIO() as to:
        call_with_retries(
            lambda: download(checksum, url, to),
            expect=ChecksumMismatch,
            max_attempts=3,
        )
        print(to.read().decode())
