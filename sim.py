"""Run the simulation."""

import argparse
import logging
import numpy.random
import time

import constants
import util

from event import *
from util import tod_to_sec, sec_to_tod

LOGGER = None

def getopts():
    defaults = {
        'log_level'    : 'WARNING',
        'days'         : 100,
        # Average time in seconds between arrival events (= 1 / mu)
        # Default: 20 per hour = 1 per 3 minutes = 180 seconds between arrivals
        'arrival_time' : 180,
    }

    parser = argparse.ArgumentParser(
        description="Simulate happy hour at Hemingway's."
    )

    parser.set_defaults(**defaults)

    parser.add_argument(
        '--days',
        type=util.positive_int_arg,
        dest='days',
        help='Number of days to simulate. (default: 100)'
    )
    parser.add_argument(
        '-l', '--log-level',
        choices='DEBUG INFO WARNING ERROR CRITICAL'.split(),
        dest='log_level',
        help='Set the global logging level. (default: WARNING)'
    )
    parser.add_argument(
        '--arrival-time',
        type=util.positive_arg,
        dest='arrival_time',
        help='The average time between customer arrivals, equal to the inverse'
             ' of the average rate.'
    )
    return parser.parse_args()

def init(opts):
    global LOGGER
    level = util.get_log_level(opts.log_level)
    if level is None:
        level = logging.WARNING
    logging.basicConfig(
        level=level,
        format='\t|\t'.join([
            # '%(asctime)s',
            '%(levelname)s',
            '%(name)s:%(lineno)d',
            '%(message)s'
        ]),
        # datefmt='%Y-%m-%d %H:%M:%S'
    )
    LOGGER = logging.getLogger('sim')
    LOGGER.info('Initialized logger (level is %s)', opts.log_level)

def main():
    global LOGGER
    opts = getopts()
    init(opts)

    stats = []
    # Main event queue, holds events of different types.
    events = EventQueue()


    start_time = time.time()

    for day in range(0, opts.days):
        events.push(HappyHourEnd(time=tod_to_sec('06:00:00 PM')))
        arrivals = 0
        for arrival in generate_arrivals(opts.arrival_time):
            events.push(arrival)
            arrivals += 1
        LOGGER.info('Generated %d arrivals', arrivals)
        del arrivals

        while events:
            event = events.pop()

            if isinstance(event, HappyHourEnd):
                # Can collect stats, clean up, etc. here
                break
            else:
                raise RuntimeError('Unhandled event: ' + str(event))
        # End of event loop

    LOGGER.info('Simulation complete (%f seconds)', time.time() - start_time)

# End of main()

def generate_arrivals(mean_time):
    """Generate customer arrivals according to an exponential distribution.

    Note that the mean parameter is the multiplicative inverse of the rate
    parameter.
    """
    time = 0
    while True:
        arrival_time = numpy.random.exponential(scale=mean_time)
        time += arrival_time
        if time + constants.HAPPY_HOUR_START < constants.HAPPY_HOUR_END:
            yield Arrival(time=time, customer=Customer())
        else:
            break
# End of generate_arrivals()

if __name__ == '__main__':
    main()
