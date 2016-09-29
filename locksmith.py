import time


class Locksmith:
    """Class which creates and distributes locks.

    Not thread safe. Best served asynchronously, via asyncio or message
    passing.
    """

    def __init__(self, default_duration=1):
        self._locks = {}
        self.default_duration = default_duration

    @classmethod
    def _expired(cls, lock, timestamp=...):
        if timestamp is ...:
            timestamp = time.time()
        return timestamp > lock['timestamp'] + lock['duration']

    def _available(self, lock_id, requester_id, timestamp=...):
        """Check whether the lock is available to the requester.

        Returns True if the lock is unassigned, expired, or already
        assigned to the requester; False otherwise.

        Because of race conditions, this method is probably not useful
        externally. Instead, try `acquire` or `release` and check the
        return value.
        """
        try:
            lock = self._locks[lock_id]
        except KeyError:
            return True
        if lock['owner'] == requester_id:
            return True
        if timestamp is ...:
            timestamp = time.time()
        return self._expired(lock, timestamp)

    def acquire(self, lock_id, requester_id, duration=...):
        """Attempt to assign a lock to a requester.

        If the lock is available, re-assigns it to the requester and
        returns True; otherwise, returns False.
        """
        now = time.time()

        if self.available(lock_id, requester_id, now):
            if duration is ...:
                duration = self.default_duration
            self._locks[lock_id] = {
                'owner': requester_id,
                'timestamp': now,
                'duration': duration,
            }
            return True
        else:
            return False

    def release(self, lock_id, owner_id):
        """Attempt to release a lock.

        If the lock previously belonged to the owner and was not already
        expired, releases the lock and returns True; otherwise, returns
        False.
        """
        try:
            lock = self._locks[lock_id]
        except KeyError:
            return False
        if lock['owner'] != owner_id:
            return False
        # Do this first to avoid race conditions
        expired = self._expired(lock)
        # Not strictly necessary if it's expired, but may as well
        del self._locks[lock_id]
        return not expired


if __name__ == '__main__':
    from zmqrpc import serve

    smith = Locksmith()

    procs = {
        'CHECK': smith.check,
        'ACQUIRE': smith.acquire,
        'RELEASE': smith.release,
    }

    serve(procs, 9001, debug=True)
