from functools import partial
import sys


def relay(readinto, consume, *, buffer=bytearray(1024)):
    r"""Relay chunks of bytes from a producer to a consumer.

    >>> from io import BytesIO

    >>> out = BytesIO()
    >>> relay(BytesIO(b'ayy lmao').readinto, out.write)
    >>> out.getvalue()
    b'ayy lmao'

    >>> relay(
    ...     readinto=BytesIO(b'ayy lmao').readinto,
    ...     consume=lambda x: print(x.tobytes()),
    ...     buffer=bytearray(2),
    ...  )
    b'ay'
    b'y '
    b'lm'
    b'ao'

    """
    assert len(buffer) > 0
    view = memoryview(buffer)
    while True:
        bytes_read = readinto(buffer)
        if not bytes_read:
            break
        # Use the memoryview to avoid copying slices.
        consume(view[:bytes_read])


class writeflush:
    def __init__(self, buffer):
        self.buffer = buffer

    def __call__(self, chunk):
        written = self.buffer.write(chunk)
        self.buffer.flush()
        return written


cat = partial(
    relay,
    readinto=sys.stdin.buffer.readinto1,
    consume=writeflush(sys.stdout.buffer),
)


class fanout(list):
    def __call__(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)


if __name__ == '__main__':
    # Echo stdin to stderr, and print the SHA-256 hash to stdout.
    from hashlib import sha256
    hasher = sha256()
    relay(
        readinto=sys.stdin.buffer.readinto1,
        consume=fanout([
            # sys.stderr.buffer.write,
            # sys.stderr.buffer.write,
            # writeflush(sys.stdout.buffer),
            writeflush(sys.stderr.buffer),
            hasher.update,
        ]),
        buffer=bytearray(2048),
    )
    print(hasher.hexdigest())
