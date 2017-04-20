"""Module for the different queues in the scenario, comprising the seating
queue, the ticket queue, and the outgoing drink queue.
"""

from collections import deque

class Queue(object):
    def __init__(self):
        self._queue = deque()

    def push(self, item):
        self._queue.appendleft(item)

    def pop(self, item):
        return self._queue.pop()

# It may be unnecessary to differentiate these, but we might want to add some
# additional logic that doesn't fit into a generic queue class.

class SeatingQueue(Queue):
    pass

class IncomingOrderQueue(Queue):
    pass

class OutgoingOrderQueue(Queue):
    pass
