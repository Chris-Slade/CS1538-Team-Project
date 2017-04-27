"""Utility functions."""

import argparse
import logging
import math

from time import strptime

HAPPY_HOUR_START = 16 * 60 * 60 # 4PM
TIME_FMT = "%I:%M:%S %p"

def tod_to_sec(tod):
    """Convert from an "absolute" time of day (e.g. "10:30:00 AM") to seconds
    since midnight.
    """
    time = strptime(tod, TIME_FMT)
    seconds_since_midnight =     \
          time.tm_hour * 60 * 60 \
        + time.tm_min * 60       \
        + time.tm_sec
    return seconds_since_midnight

def sec_to_tod(sec):
    """Convert from the offset in seconds from midnight to an absolute time of
    day, suitable for printing.
    """
    assert sec >= 0, 'Sec cannot be negative'
    hours = (sec // (60*60)) % 24
    mins  = (sec // 60) % 60
    secs  = sec % 60
    if hours > 12:
        hours -= 12
    elif hours == 0:
        hours = 12
    return '{:02.0f}:{:02.0f}:{:02.0f} {}'.format(
        hours,
        mins,
        secs,
        "PM" if sec >= 12*60*60 else "AM"
    )

def get_log_level(level_str):
    try:
        level = getattr(logging, level_str)
        if not isinstance(level, int):
            raise AttributeError('Dummy')
        return level
    except AttributeError:
        return None

def positive_int_arg(value):
    try:
        value = int(value)
        if value > 0:
            return value
        raise ValueError()
    except ValueError:
        raise argparse.ArgumentTypeError('argument must be a positive integer')

def positive_arg(value):
    try:
        if '.' in value:
            value = float(value)
        else:
            value = int(value)
        if value > 0:
            return value
        raise ValueError()
    except ValueError:
        raise argparse.ArgumentTypeError('argument must be positive')

class Averager(object):
    """A class for efficiently computing statistics of large data sets.

    Uses Welford's algorithm, adapted from
    en.wikipedia.org/wiki/Algorithms_for_calculating_variance#Online_algorithm
    """

    def __init__(self):
        self.n  = 0
        self.a  = 0.0
        self.M2 = 0.0

    def add(self, x):
        self.n  += 1
        d1      =  x - self.a
        self.a  += d1 / self.n
        d2      =  x - self.a
        self.M2 += d1 * d2

    def get_mean(self):
        return self.a

    def get_variance(self):
        if self.n < 2:
            return float('NaN')
        else:
            return self.M2 / (self.n - 1)

    def get_stddev(self):
        return math.sqrt(self.get_variance())

    def get_n(self):
        return self.n

    def __repr__(self):
        return '{{ "n" : {:d}, "mean" : {:f}, "stddev" : {:f} }}'.format(
            self.n,
            self.a,
            self.get_stddev()
        )

    def __str__(self):
        return str(self.a)
