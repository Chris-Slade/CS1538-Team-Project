"""Run the simulation."""

import argparse
import logging
import time

import constants
import util

LOGGER = None

def getopts():
    defaults = {
        'log_level' : 'WARNING',
        'days'      : 100,
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
        # TODO: Generate arrival events, put into event queue

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

if __name__ == '__main__':
    main()
