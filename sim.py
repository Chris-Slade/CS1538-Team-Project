"""Run the simulation."""

import argparse
import logging
import numpy.random
import time

import constants
import person
import queues
import util

from bar import Bar
from event import *
from util import tod_to_sec, sec_to_tod

LOGGER = None

def getopts():
    """Parse program command line arguments."""
    defaults = {
        'log_level'    : 'WARNING',
        'days'         : 1,
        # Average time in seconds between arrival events (= 1 / mu)
        # Default: 20 per hour = 1 per 3 minutes = 180 seconds between arrivals
        'arrival_time' : 180,
        'num_servers'  : 2,
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
    parser.add_argument(
        '--num-servers',
        type=util.positive_int_arg,
        dest='num_servers',
        help='The number of servers.'
    )
    return parser.parse_args()

def init(opts):
    """Initialize the global state of the sim, such as the logger."""
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
    """Entry point of the simulation program."""
    global LOGGER
    opts = getopts()
    init(opts)
    start_time = time.time()

    stats = []

    for day in range(0, opts.days):
        # Main event queue, holds events of different types.
        events = EventQueue()
        # Bar
        bar = Bar()
        # Various queues
        seating_queue = queues.SeatingQueue()
        incoming_orders = queues.OrderQueue()
        outgoing_orders = queues.DrinkQueue()
        # Stats collection
        stats.append({})

        # Add an event signaling the end of happy hour
        events.push(HappyHourEnd(time=constants.HAPPY_HOUR_END))

        # Generate customer arrival events
        stats[day]['arrivals'] = 0
        for arrival in generate_arrivals(opts.arrival_time):
            events.push(arrival)
            stats[day]['arrivals'] += 1
        LOGGER.info('Generated %d arrivals', stats[day]['arrivals'])

        # Set up initial server idle events
        for _ in range(0, opts.num_servers):
            events.push(
                ServerIdle(
                    time=constants.HAPPY_HOUR_START,
                    server=person.Server()
                )
            )

        while events:
            event = events.pop()

            if isinstance(event, HappyHourEnd):
                # Can collect stats, clean up, etc. here
                break
            elif isinstance(event, Arrival):
                LOGGER.info(
                    '%s added to seating queue at %s',
                    str(event.get_person()),
                    sec_to_tod(event.get_time())
                )
                seating_queue.push(event.get_person())
            elif isinstance(event, ServerIdle):
                ... # TODO
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
            yield Arrival(
                time=time + constants.HAPPY_HOUR_START,
                person=person.Customer()
            )
        else:
            break
# End of generate_arrivals()

if __name__ == '__main__':
    main()
