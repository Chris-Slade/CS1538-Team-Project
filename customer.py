import numpy.random
from constants import DRINKS_ORDERED_MEAN,DRINKS_ORDERED_STD_DEV
class Customer(object):

    def __init__(self):
        self._drinks_wanted = Customer.decide_drinks_wanted()

    @staticmethod
    def decide_drinks_wanted():
        return int(abs(round(numpy.random.normal(DRINKS_ORDERED_MEAN, DRINKS_ORDERED_STD_DEV))))
