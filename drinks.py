import math
import numpy.random

from enum import Enum
from random import random as rand

import person

# TODO: Review the preparation times for the different drink types and the
# frequency with which each type is ordered.

Drink = Enum('Drink', 'tap cocktail pitcher')

Drink.avg_prep_time = lambda self: \
         15 if self == Drink.tap      \
    else 25 if self == Drink.cocktail \
    else 45 if self == Drink.pitcher  \
    else None

Drink.prep_time = lambda self: numpy.random.normal(
    loc=self.avg_prep_time(),
    scale=math.sqrt(self.avg_prep_time())
)

def random_drink():
    choice = rand()
    if choice < 0.5:
        return Drink.tap
    elif choice < 0.8:
        return Drink.cocktail
    else:
        return Drink.pitcher
