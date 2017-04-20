import numpy.random

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
        return int(abs(round(numpy.random.normal(2, 1))))

class Server(Person):
    ... # TODO

class Bartender(Person):
    ... # TODO
