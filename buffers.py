from functools import partial
import hashlib
import sys


def chunks(readinto, buffer):
    r"""Read chunks of bytes into the provided buffer.

    Yields memoryview slices of the buffer to avoid unnecessary copies.

    >>> from io import BytesIO

    >>> input = BytesIO(b'ayy lmao')
    >>> buffer = bytearray(3)
    >>> for chunk in chunks(input.readinto, buffer):
    ...     print(buffer, chunk.tobytes())
    bytearray(b'ayy') b'ayy'
    bytearray(b' lm') b' lm'
    bytearray(b'aom') b'ao'

    """
    assert len(buffer) > 0
    view = memoryview(buffer)
    while True:
        bytes_read = readinto(buffer)
        if not bytes_read:
            break
        # Slice the memoryview to avoid copying data from the buffer.
        yield view[:bytes_read]


def relay(readinto, consume, *, buffer=None):
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
    if buffer is None:
        buffer = bytearray(2048)
    for chunk in chunks(readinto, buffer):
        consume(chunk)


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


def multihash(names, stream, **kwargs):
    """Compute multiple hashes in a single pass.

    >>> from io import BytesIO
    >>> hashes = multihash(['md5', 'sha1', 'sha256'], BytesIO(b'ayy lmao'))
    >>> for name, digest in hashes.items():
    ...     print(f"{name}: {digest}")
    md5: 2b14f6a69199243f570031bf94865bb6
    sha1: 1ac4eb815f2b72da8fe50cc44f236a41368c121c
    sha256: 363bd719f9697e46e6514bf1f0efce0e5ace75683697fb820065a05c8fb3135e
    """
    hashers = [hashlib.new(name) for name in names]
    consume = fanout([hasher.update for hasher in hashers])
    relay(readinto=stream.readinto, consume=consume, **kwargs)
    return {name: hasher.hexdigest() for name, hasher in zip(names, hashers)}


if __name__ == '__main__':
    # Echo stdin to stderr, and print several hashes to stdout.
    names = ['md5', 'sha1', 'sha256']
    hashers = [hashlib.new(name) for name in names]
    relay(
        readinto=sys.stdin.buffer.readinto1,
        consume=fanout([
            # sys.stderr.buffer.write,
            # sys.stderr.buffer.write,
            # writeflush(sys.stdout.buffer),
            writeflush(sys.stderr.buffer),
            *[hasher.update for hasher in hashers],
        ]),
    )
    for name, hasher in zip(names, hashers):
        print(f"{name}: {hasher.hexdigest()}")
