import math
import numpy.random

from collections import namedtuple
from random import random as rand

import person

class Drink(object):
    avg_prep_time    = 20     # seconds, derived from data
    stddev_prep_time = 7.3048 # seconds, derived from data

    @staticmethod
    def prep_time():
        return numpy.random.normal(
            loc=Drink.avg_prep_time,
            scale=math.sqrt(Drink.avg_prep_time)
        )

Order = namedtuple('Order', 'customer time_placed')
