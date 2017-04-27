import numpy.random

import constants

from constants import AVG_DRINKS_WANTED, STDDEV_DRINKS_WANTED

class Person(object):
    _number = 1

    def __init__(self):
        self._number = self.__class__._number
        self.__class__._number += 1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{} {:d}".format(self.__class__.__name__, self._number)

    def get_number(self):
        return self._number

    @classmethod
    def reset_numbers(cl):
        cl._number = 1

class Customer(Person):
    def __init__(self, arrival_time):
        super().__init__()
        self._drinks_wanted = Customer.decide_drinks_wanted()
        self._arrival_time = arrival_time

    @staticmethod
    def decide_drinks_wanted():
        drinks_wanted = int(abs(round(
            numpy.random.normal(
                AVG_DRINKS_WANTED,
                STDDEV_DRINKS_WANTED
            )
        )))
        if drinks_wanted == 0:
            drinks_wanted = 1
        return drinks_wanted

    def drinks_wanted(self):
        """Get the number of drinks the customer wants."""
        return self._drinks_wanted

    def drink(self):
        """Make the customer drink (i.e. decrement drinks wanted)."""
        self._drinks_wanted -= 1

    def get_arrival_time(self):
        return self._arrival_time

class Server(Person):
    def __init__(self, skill=1):
        super().__init__()
        self._skill = skill

    def get_skill(self):
        return self._skill

    @staticmethod
    def get_seating_time(avg_time=constants.AVG_SEATING_TIME):
        return int(abs(round(
            numpy.random.exponential(avg_time)
        )))

class Bartender(Person):
    def __init__(self):
        super().__init__()
