"""Time-based One-Time Passwords.

Inspired by https://github.com/susam/mintotp
"""
import hmac
import time
from dataclasses import dataclass


@dataclass
class OTPGenerator:
    """
    See https://datatracker.ietf.org/doc/html/rfc2104
    See https://datatracker.ietf.org/doc/html/rfc4226
    See https://datatracker.ietf.org/doc/html/rfc6238
    """
    key: bytes
    time_step: int = 30
    digits: int = 6
    digest: str = 'sha1'

    @classmethod
    def from_b32(cls, b32: str, **kwargs):
        return cls(cls.decode(b32), **kwargs)

    @staticmethod
    def decode(b32: str) -> bytes:
        from base64 import b32decode
        padding = '=' * ((8 - len(b32)) % 8)
        return b32decode(b32 + padding, casefold=True)

    def hotp(self, counter: int) -> str:
        """HMAC-based One-Time Password.

           HOTP(K,C) = Truncate(HMAC-SHA-1(K,C))

        See https://datatracker.ietf.org/doc/html/rfc4226#section-5
        """
        assert counter >= 0, counter
        hmac_result = self._hmac(counter)
        truncated = self._truncate(hmac_result)
        reduced = self._reduce(truncated)
        return reduced

    def _hmac(self, counter: int) -> bytes:
        return hmac.digest(
            key=self.key,
            msg=counter.to_bytes(8, 'big'),
            digest=self.digest)

    def _truncate(self, hmac_result: bytes) -> int:
        """
        From the RFC:

        "The purpose of the dynamic offset truncation technique is to
        extract a 4-byte dynamic binary code from a 160-bit (20-byte)
        HMAC-SHA-1 result."
        """
        # Use the low-order 4 bits of the final byte as an offset.
        offset = hmac_result[-1] & 0xf
        # Extract the 4-byte "dynamic binary code" at the offset.
        P = hmac_result[offset:offset+4]
        # Return the last 31 bits of P (mask off the leftmost bit).
        bin_code = int.from_bytes(P, 'big') & 0x7fffffff
        return bin_code

    def _reduce(self, code: int) -> str:
        """Convert a 4-byte "dynamic binary code" to base-10 digits."""
        str_code = str(code).zfill(self.digits)
        return str_code[-self.digits:]

    def counter(self, time: float) -> int:
        return int(time / self.time_step)

    def totp(self, time: float) -> str:
        """Time-based One-Time Password.

        See https://datatracker.ietf.org/doc/html/rfc6238#section-4
        """
        return self.hotp(self.counter(time))

    def current(self, *, clock=time.time) -> str:
        return self.totp(clock())


def totp(key_b32: str):
    return OTPGenerator.from_b32(key_b32).current()


if __name__ == '__main__':
    import sys

    keys = sys.argv[1:]

    if keys:
        for key in keys:
            print(totp(key))
    else:
        from mintotp import hotp

        for exp in reversed(range(10, 64)):
            start = int(2**exp) - 2**10
            stop = start + 2**11
            for key in ['', 'ayyy', 'lmao']:
                gen = OTPGenerator.from_b32(key)
                for counter in reversed(range(start, stop)):
                    mine = gen.hotp(counter)
                    theirs = hotp(key, counter)
                    assert mine == theirs, (key, counter, mine, theirs)
