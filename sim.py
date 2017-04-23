"""Run the simulation."""

import argparse
import logging
import numpy.random
import time as time_mod

from collections import deque, defaultdict
from random import random as rand

import constants
import person
import util

from bar import Bar
from event import *
from util import tod_to_sec, sec_to_tod

LOGGER = None

def getopts():
    """Parse program command line arguments.

    Options get their default settings from the values in constants.py. If an
    option is specified on the command line, it will take precedence over the
    default definition.
    """
    defaults = {
        'log_level'             : 'WARNING',
        'days'                  : 1,
        'arrival_time'          : constants.AVG_ARRIVAL_TIME,
        'num_servers'           : constants.NUM_SERVERS,
        'num_bartenders'        : constants.NUM_BARTENDERS,
        'num_bar_seats'         : constants.NUM_BAR_SEATS,
        'seating_time'          : constants.AVG_SEATING_TIME,
        'delivery_time'         : constants.AVG_DRINK_DELIVERY_TIME,
        'drink_time'            : constants.AVG_DRINK_TIME,
        'drinks_wanted_mean'    : constants.DRINKS_WANTED_MEAN,
        'drinks_wanted_std_dev' : constants.DRINKS_WANTED_STD_DEV,
    }

    parser = argparse.ArgumentParser(
        description="Simulate happy hour at Hemingway's."
    )

    parser.set_defaults(**defaults)

    parser.add_argument(
        '--days',
        type=util.positive_int_arg,
        dest='days',
        help='Number of days to simulate. (default: %s)' % defaults['days']
    )
    parser.add_argument(
        '-l', '--log-level',
        choices='DEBUG INFO WARNING ERROR CRITICAL'.split(),
        dest='log_level',
        help='Set the global logging level. (default: %s)' % defaults['log_level']
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
    parser.add_argument(
        '--num-bartenders',
        type=util.positive_int_arg,
        dest='num_bartenders',
        help='The number of bartenders.'
    )
    parser.add_argument(
        '--num-bar-seats',
        type=util.positive_int_arg,
        dest='num_bar_seats',
        help='The number of seats at the bar.'
    )
    parser.add_argument(
        '--seating-time',
        type=util.positive_arg,
        dest='seating_time',
        help='The average time it takes to be seated by a server.'
    )
    parser.add_argument(
        '--delivery-time',
        type=util.positive_arg,
        dest='delivery_time',
        help='The average time it takes for a server to deliver a prepared'
            ' drink.'
    )
    parser.add_argument(
        '--drink-time',
        type=util.positive_arg,
        dest='drink_time',
        help='The average time it takes to drink a drink.'
    )
    parser.add_argument(
        '--drinks-wanted-mean',
        type=util.positive_arg,
        dest='drinks_wanted_mean',
        help='The average number of drinks wanted.'
    )
    parser.add_argument(
        '--drinks-wanted-std-dev',
        type=util.positive_arg,
        dest='drinks_wanted_std_dev',
        help='The standard deviation of drinks wanted.'
    )

    opts = parser.parse_args()

    # Override constants with those changed in the command line options.
    constants.AVG_ARRIVAL_TIME        = opts.arrival_time
    constants.NUM_SERVERS             = opts.num_servers
    constants.NUM_BARTENDERS          = opts.num_bartenders
    constants.NUM_BAR_SEATS           = opts.num_bar_seats
    constants.AVG_SEATING_TIME        = opts.seating_time
    constants.AVG_DRINK_TIME          = opts.drink_time
    constants.AVG_DRINK_DELIVERY_TIME = opts.delivery_time
    constants.DRINKS_WANTED_MEAN      = opts.drinks_wanted_mean
    constants.DRINKS_WANTED_STD_DEV   = opts.drinks_wanted_std_dev

    return opts
# End of getopts()

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

    cons = {}
    for constant in dir(constants):
        if constant[0].isupper():
            cons[constant] = getattr(constants, constant)
    LOGGER.info(cons)
    del cons

    stats = []

    for day in range(0, opts.days):
        # Main event queue, holds events of different types.
        events = EventQueue()
        # Bar
        bar = Bar(num_seats=opts.num_bar_seats)
        # Various queues
        seating_queue   = deque()
        incoming_orders = deque()
        outgoing_orders = deque()
        # Stats collection
        stats.append({
            'arrivals' : 0,
            'drinks_served' : 0,
            'server_idle_time' : defaultdict(int),
            'seating_wait_time' : util.Averager(),
            'drink_wait_time' : util.Averager(),
        })

        # Add an event signaling the end of happy hour
        events.push(HappyHourEnd(time=constants.HAPPY_HOUR_END))

        # Generate customer arrival events
        for arrival in generate_arrivals(opts.arrival_time):
            events.push(arrival)
            stats[day]['arrivals'] += 1
        LOGGER.info('Generated %d arrivals', stats[day]['arrivals'])

        # Set up initial server and bartender idle events
        for _ in range(0, opts.num_servers):
            events.push(
                ServerIdle(
                    time=constants.HAPPY_HOUR_START,
                    server=person.Server()
                )
            )
        for _ in range(0, opts.num_bartenders):
            events.push(
                BartenderIdle(
                    time=constants.HAPPY_HOUR_START,
                    bartender=person.Bartender()
                )
            )

        while events:
            event = events.pop()

            if isinstance(event, HappyHourEnd):
                LOGGER.info(event)
                # Can collect stats, clean up, etc. here
                break
            elif isinstance(event, Arrival):
                LOGGER.info(event)
                seating_queue.appendleft(event.get_person())
            elif isinstance(event, ServerIdle):
                # If both queues are empty, wait around for 30 seconds
                if (
                    (not seating_queue or bar.available_seats() <= 0)
                    and not outgoing_orders
                ):
                    LOGGER.debug(
                        '%s has nothing to do at %s',
                        event.get_server(),
                        sec_to_tod(event.get_time())
                    )
                    events.push(
                        ServerIdle(
                            time=event.get_time() + 30,
                            server=event.get_server()
                        )
                    )
                    stats[day]['server_idle_time'][
                        event.get_server().get_number()
                    ] += 30
                    continue

                # Take a customer from the seating queue and seat him at the
                # bar.
                if (
                    bar.available_seats() > 0
                    and handle_seating_queue(
                        len(seating_queue),
                        len(outgoing_orders)
                    )
                ):
                    time        = event.get_time()
                    server      = event.get_server()
                    time_offset = person.Server.get_seating_time(opts.seating_time)
                    customer    = seating_queue.pop()
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
                    LOGGER.debug('Bar: %s', bar)
                    # Server becomes idle after seating the customer.
                    events.push(ServerIdle(time=time + time_offset, server=server))
                    stats[day]['seating_wait_time'].add(
                        time + time_offset - customer.get_arrival_time()
                    )
                    LOGGER.info(
                        '%s was taken from seating line by %s at %s to be'
                        ' seated at %s',
                        str(customer),
                        str(server),
                        sec_to_tod(time),
                        sec_to_tod(time + time_offset)
                    )
                    # Clean namespace
                    del time, server, time_offset, customer
                # If not handling the seating queue, handle the outgoing drink
                # queue.
                else:
                    LOGGER.info(
                        '%s is serving drinks at %s',
                        event.get_server(),
                        sec_to_tod(event.get_time())
                    )
                    assert outgoing_orders, 'No outgoing orders!'
                    # Server takes the order from the outgoing queue...
                    order = outgoing_orders.pop()
                    delivery_time = numpy.random.exponential(opts.delivery_time)
                    # ... and delivers it to the customer
                    events.push(
                        DeliverDrink(
                            time=event.get_time() + delivery_time,
                            customer=order.customer
                        )
                    )
                    # Track average wait time for a drink
                    stats[day]['drink_wait_time'].add(
                        # Time for a drink to be served = time of
                        # DrinkDelivered event minus the time the order was
                        # placed.
                        event.get_time() + delivery_time - order.time_placed
                    )
                    events.push(
                        ServerIdle(
                            time=event.get_time() + delivery_time,
                            server=event.get_server()
                        )
                    )
                    del order

            elif isinstance(event, OrderDrink):
                LOGGER.info(event)
                incoming_orders.appendleft(
                    drinks.Order(
                        customer=event.get_customer(),
                        drink_type=event.drink_type(),
                        time_placed=event.get_time()
                    )
                )

            elif isinstance(event, BartenderIdle):
                # Wait around for 30 seconds if there are no incoming orders.
                if not incoming_orders:
                    events.push(
                        BartenderIdle(time=event.get_time() + 30,
                        bartender=event.get_bartender())
                    )
                    continue
                # Otherwise take an order and prepare it.
                order = incoming_orders.pop()
                assert isinstance(order.customer, person.Customer)
                assert isinstance(order.drink_type, drinks.Drink)
                LOGGER.info(
                    '%s is preparing a %s drink for %s at %s',
                    event.get_bartender(),
                    order.drink_type.name,
                    order.customer,
                    sec_to_tod(event.get_time())
                )
                prep_time = order.drink_type.prep_time()
                events.push(
                    PreppedDrink(
                        time=event.get_time() + prep_time,
                        order=order
                    )
                )
                events.push(
                    BartenderIdle(
                        time=event.get_time() + prep_time,
                        bartender=event.get_bartender()
                    )
                )
                del order

            elif isinstance(event, PreppedDrink):
                LOGGER.info(event)
                outgoing_orders.appendleft(event.get_order())

            elif isinstance(event, DeliverDrink):
                customer = event.get_customer()
                customer.drink() # Decrement drinks wanted
                stats[day]['drinks_served'] += 1
                drink_time = numpy.random.exponential(opts.drink_time)
                LOGGER.info(
                    '%s served drink at %s',
                    customer,
                    sec_to_tod(event.get_time())
                )
                if customer.drinks_wanted() > 0:
                    events.push(
                        OrderDrink(
                            time=event.get_time() + drink_time,
                            customer=customer,
                            drink_type=drinks.random_drink()
                        )
                    )
                else:
                    # Customer leaves after drinking last drink
                    events.push(
                        Departure(
                            time=event.get_time() + drink_time,
                            customer=customer
                        )
                    )

                del customer, drink_time

            elif isinstance(event, Departure):
                LOGGER.info(event)
                LOGGER.debug('Bar: %s', bar)
                bar.remove_customer(event.get_customer())

            else:
                raise RuntimeError('Unhandled event: ' + str(event))
        # End of event loop

    LOGGER.info(
        'Simulation complete (%f seconds)',
        time_mod.time() - start_time
    )

    print(stats)

# End of main()

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
        time_of_day = time + constants.HAPPY_HOUR_START
        if time_of_day < constants.HAPPY_HOUR_END:
            yield Arrival(
                time=time_of_day,
                customer=person.Customer(arrival_time=time_of_day)
            )
        else:
            break
# End of generate_arrivals()

if __name__ == '__main__':
    main()
