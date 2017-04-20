"""Classes of events in the simulation, and an event queue."""

import heapq

import util

from person import Person

class EventQueue(object):
    """A priority queue for Events."""

    def __init__(self):
        self._queue = []

    def push(self, event):
        """Add an event to the queue."""
        assert isinstance(event, Event), \
            'Cannot push non-event ({}) to event queue'.format(type(event))
        heapq.heappush(self._queue, event)

    def pop(self):
        return heapq.heappop(self._queue)

    def peek(self):
        return self._queue[0]

    def clear(self):
        self._queue.clear()

    def __len__(self):
        return self._queue.__len__()

    def __iter__(self):
        return self._queue.__iter__()

    def __str__(self):
        return self._queue.__str__()

################################### Events ####################################

class Event(object):
    """An event in the simulation.

    Every event has a time, which is a nonnegative number.

    Comparisons between events are done on the event times. To compare
    identity, use the `is` operator.
    """

    def __init__(self, time):
        assert time >= 0, "Can't have negative time"
        self._time = time

    def get_time(self):
        return self._time

    def __eq__(self, other):
        return self._time == other._time

    def __lt__(self, other):
        return self._time < other._time

    def __le__(self, other):
        return self._time <= other._time

    def __gt__(self, other):
        return self._time > other._time

    def __ge__(self, other):
        return self._time >= other._time

    def __repr__(self):
        return '<{}: {}>'.format(
            self.__class__.__name__,
            util.sec_to_tod(self._time)
        )

class TimeEvent(Event):
    """A generic event that can be used to indicate special times (such as the
    turn of an hour).
    """
    pass

class HappyHourEnd(Event):
    """Event for when happy hour ends."""
    pass

########################### Events that have people ###########################

class PersonEvent(Event):
    """An event with a person, which has a reference in the event object."""

    def __init__(self, time, person):
        super().__init__(time=time)
        assert person is None or isinstance(person, Person), \
            'Need a person'
        self._person = person

    def get_person(self):
        return self._person

    def __repr__(self):
        return '<{}: {} at {}>'.format(
            self.__class__.__name__,
            self._person,
            util.sec_to_tod(self._time)
        )

############################### Customer Events ###############################

class CustomerEvent(PersonEvent):
    pass

class Arrival(CustomerEvent):
    """Customer arrived."""
    pass

################################ Server Events ################################

class ServerEvent(PersonEvent):
    def __init__(self, time, server):
        super().__init__(time=time, person=server)

class ServerIdle(ServerEvent):
    pass

class SeatCustomer(ServerEvent):
    """Server gives a customer a seat."""
    pass