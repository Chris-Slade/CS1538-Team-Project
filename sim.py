"""Run the simulation."""

import argparse
import logging
import numpy.random
import time as time_mod

from random import random as rand

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
    start_time = time_mod.time()

    stats = []

    for day in range(0, opts.days):
        # Main event queue, holds events of different types.
        events = EventQueue()
        # Bar
        bar = Bar()
        # Various queues
        seating_queue = queues.SeatingQueue()
        incoming_orders = queues.IncomingOrderQueue()
        outgoing_orders = queues.OutgoingOrderQueue()
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
                LOGGER.info(event)
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
                # If both queues are empty, wait around for 30 seconds
                if not seating_queue and not outgoing_orders:
                    events.push(
                        ServerIdle(
                            time = event.get_time() + 30,
                            server=event.get_server()
                        )
                    )
                    continue

                time        = event.get_time()
                server      = event.get_server()
                time_offset = None
                customer    = None

                # Take a customer from the seating queue and seat him at the
                # bar.
                if (
                    bar.available_seats() > 0
                    and handle_seating_queue(
                        len(seating_queue),
                        len(outgoing_orders)
                    )
                ):
                    time_offset = random_seating_time()
                    customer = seating_queue.pop()
                    assert customer.drinks_wanted() >= 1, \
                        "New arrival doesn't want any drinks"
                    # Customer orders a drink after being seated.
                    events.push(
                        OrderDrink(
                            time=time + time_offset,
                            customer=customer,
                            drink_type=drinks.random_drink()
                        )
                    )
                    # Seat is taken at the start of the seating process to
                    # prevent it from being preempted.
                    bar.seat_customer(customer)
                    # Server becomes idle after seating the customer.
                    events.push(ServerIdle(time=time + time_offset, server=server))
                    LOGGER.info(
                        '%s was taken from seating line by %s at %s to be'
                        ' seated at %s',
                        str(customer),
                        str(server),
                        sec_to_tod(time),
                        sec_to_tod(time + time_offset)
                    )
                # If not handling the seating queue, handle the outgoing drink
                # queue.
                else:
                    ... # TODO
                # Clean namespace
                del time, time_offset, customer, server

            elif isinstance(event, OrderDrink):
                LOGGER.info(event)
                incoming_orders.push(
                    ( event.get_customer(), event.drink_type() )
                )

            else:
                raise RuntimeError('Unhandled event: ' + str(event))
        # End of event loop

    LOGGER.info(
        'Simulation complete (%f seconds)',
        time_mod.time() - start_time
    )

# End of main()

def random_seating_time(avg_seating_time=constants.AVG_SEATING_TIME):
    return numpy.random.exponential(avg_seating_time)

def handle_seating_queue(waiting_customers, outgoing_orders):
    """Choose whether to handle the seating queue or the outgoing order queue.

    If there are X customers waiting for seating and Y outgoing orders, the
    probability of the server choosing to seat a customer is X / (X + Y). This
    has some nice properties, namely that the limit as X goes to infinity is
    1, the limit as Y goes to infinity is 0, and when either goes to 0 the
    probability of choosing the opposite approaches 1.

    Arguments:

    - waiting_customers: The number of customers waiting to be seated (i.e. the
      length of the seating queue).
    - outgoing_orders: The number of orders ready to be delivered (i.e. the
      length of the outgoing order queue).
    """
    return rand() < waiting_customers / (waiting_customers + outgoing_orders)

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
                customer=person.Customer()
            )
        else:
            break
# End of generate_arrivals()

if __name__ == '__main__':
    main()
