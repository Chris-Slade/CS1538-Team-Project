import numpy.random

import constants

from constants import DRINKS_WANTED_MEAN, DRINKS_WANTED_STD_DEV

class Person(object):
    _number = 1

    def __init__(self):
        self._number = self.__class__._number
        self.__class__._number += 1

    def __repr__(self):
        return str(self)

    def __str__(self):
        return "{} {:3d}".format(self.__class__.__name__, self._number)

class Customer(Person):
    def __init__(self):
        super().__init__()
        self._drinks_wanted = Customer.decide_drinks_wanted()

    @staticmethod
    def decide_drinks_wanted():
        drinks_wanted = int(abs(round(
            numpy.random.normal(
                DRINKS_WANTED_MEAN,
                DRINKS_WANTED_STD_DEV
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

class Server(Person):
    def __init__(self, skill=1):
        super().__init__()
        self._skill = skill

    def get_skill(self):
        return self._skill

    @staticmethod
    def get_seating_time():
        return int(abs(round(
            numpy.random.exponential(constants.AVG_SEATING_TIME)
        )))

class Bartender(Person):
    def __init__(self):
        super().__init__()
