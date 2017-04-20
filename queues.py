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

class SeatingQueue(Queue):
    pass

class TicketQueue(Queue):
    pass

class DrinkQueue(Queue):
    pass
