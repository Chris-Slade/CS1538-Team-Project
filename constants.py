"""Constants that are relevant to the simulation."""

import util

HAPPY_HOUR_START = util.tod_to_sec('04:00:00 PM')
HAPPY_HOUR_END = util.tod_to_sec('06:00:00 PM')
NUM_BAR_SEATS = 20
AVG_SEATING_TIME = 30 # seconds
AVG_DRINK_TIME = 15 # seconds
DRINKS_WANTED_MEAN = 2
DRINKS_WANTED_STD_DEV = 1
