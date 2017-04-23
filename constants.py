"""Constants that are relevant to the simulation."""

import util

HAPPY_HOUR_START = util.tod_to_sec('04:00:00 PM')
HAPPY_HOUR_END = util.tod_to_sec('06:00:00 PM')

NUM_SERVERS = 2

NUM_BARTENDERS = 2

# How long servers and bartenders wait (in seconds) before trying to do
# something again when there's nothing to do. (wwi = wait when idle.)
SERVER_WWI = 30
BARTENDER_WWI = 30

NUM_BAR_SEATS = 20

# Average time in seconds between arrival events (= 1 / mu) Default: 20 per
# hour = 1 per 3 minutes = 180 seconds between arrivals.
AVG_ARRIVAL_TIME = 180

AVG_SEATING_TIME = 30 # seconds

AVG_DRINK_TIME = 120 # seconds

AVG_DRINK_DELIVERY_TIME = 30 # seconds

DRINKS_WANTED_MEAN = 2
DRINKS_WANTED_STD_DEV = 1
