"""Utility functions."""

import argparse
import logging

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
