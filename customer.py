import numpy.random

class Customer(object):

    def __init__(self):
        self._drinks_wanted = Customer.decide_drinks_wanted()

    @staticmethod
    def decide_drinks_wanted():
        return int(abs(round(numpy.random.normal(2, 1))))
