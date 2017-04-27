"""Compute nicer statistics from the output of sim.py.

Tip: If you have the util-linux package installed, try running this as

    python calc_stats.py 2s_2b.json | column -t -s $'\t'

to get even nicer output.
"""

import json
import sys

import util

if len(sys.argv) < 2:
    print('Need file')
    sys.exit()

def show_idle_time(key, days):
    persons = {}
    for day in days:
        for person in day[key + '_idle_time']:
            if person not in persons:
                persons[person] = util.Averager()
            else:
                persons[person].add(day[key + '_idle_time'][person])
    print('Number of {}s:\t{}'.format(key, len(persons)))
    for person in persons:
        print(
            'Average idle time ({} {}):\t{:.4f} seconds'.format(
                key,
                person,
                persons[person].get_mean()
            )
        )
        print(
            'Percentage of time spent idle ({} {}):\t{:.4f}'.format(
                key,
                person,
                100 * (persons[person].get_mean() / 7200)
            )
        )
        print(
            'Std. dev. idle time ({} {}):\t{:.4f} seconds'.format(
                key,
                person,
                persons[person].get_stddev()
            )
        )

def avg_wait_time(key, days):
    n = sum(day[key]['n'] for day in days)
    avg = 0
    for day in days:
        mean = day[key]['mean']
        weight = day[key]['n']
        avg += mean * weight
    avg /= n
    return (n, avg)

with open(sys.argv[1], 'r') as fp:
    days = json.load(fp)

    (swt_n, swt_avg) = avg_wait_time('seating_wait_time', days)
    (dwt_n, dwt_avg) = avg_wait_time('drink_wait_time', days)

    avg_customers = util.Averager()
    for day in days:
        avg_customers.add(day['arrivals'])

    avg_drinks = util.Averager()
    for day in days:
        avg_drinks.add(day['drinks_served'])

    print('Days:', len(days), sep='\t')
    print('Total customers seated:', swt_n, sep='\t')
    print('Average customer arrivals:\t{:.4f}'.format(avg_customers.get_mean()))
    print('Average seating time:\t{:.4f} seconds'.format(swt_avg))
    print('Total drinks served:', dwt_n, sep='\t')
    print('Average drinks served:\t{:.4f}'.format(avg_drinks.get_mean()))
    print('Average drink wait time:\t{:.4f} seconds'.format(dwt_avg))
    show_idle_time('server', days)
    show_idle_time('bartender', days)
