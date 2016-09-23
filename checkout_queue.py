import heapq
import time
from collections import deque
from itertools import count


class CheckoutQueue:
    """Queue that waits for confirmation before removing items.

    Instead of just popping an item, a client "checks out" an item for a
    specified duration, during which it is unavailable to other clients.
    The client must then separately signal the "completion" of that item
    within the duration (according to the queue's reckoning), or else
    the item *may* be returned to the front of the queue and checked out
    to another client. (The current implementation only guarantees this
    behavior if the queue receives another checkout request after the
    item's deadline but before the item is completed.)

    This class is not thread safe. Use asyncio or a message passing
    system for concurrent access.
    """

    def __init__(self, clock=time.monotonic):
        self.clock = clock
        self.ids = count()
        self._todo = deque()
        self._deadlines = []  # heap of (deadline, id)
        self._checked_out = {}

    def put(self, obj):
        self._todo.append((next(self.ids), obj))

    def checkout(self, duration=1):
        self._collect_overdue()
        id, obj = self._todo.popleft()
        deadline = self.clock() + duration
        heapq.heappush(self._deadlines, (deadline, id))
        self._checked_out[id] = obj
        return id, obj

    def complete(self, id):
        try:
            self._checked_out.pop(id)
        except KeyError:
            return False
        else:
            return True

    def _collect_overdue(self):
        while True:
            try:
                # Get the checked-out task with the earlist deadline
                deadline, id = self._deadlines[0]
            except IndexError:
                # No tasks have been checked out; we're done
                return
            if self.clock() < deadline:
                # The task is not overdue; we're done
                return
            else:
                # The task is overdue
                heapq.heappop(self._deadlines)
                try:
                    obj = self._checked_out.pop(id)
                except KeyError:
                    # The task was already completed;
                    # continue on to the next one
                    continue
                else:
                    # Return the task to the start of the to-do list
                    self._todo.appendleft((id, obj))
                    # We only need to do this once for each checkout
                    # in order to prevent starvation
                    return
