"""Unit tests for util.py."""

import argparse
import unittest

from util import *

class TestUtil(unittest.TestCase):

    def test_tod_to_sec_am(self):
        self.assertEqual(tod_to_sec('10:30:05 AM'), 10*60*60 + 30*60 + 5)

    def test_tod_to_sec_midnight(self):
        self.assertEqual(tod_to_sec('12:00:00 AM'), 0)

    def test_tod_to_sec_pm(self):
        self.assertEqual(tod_to_sec('02:30:05 PM'), 14*60*60 + 30*60 + 5)

    def test_sec_to_tod_am(self):
        self.assertEqual(sec_to_tod(10*60*60 + 30*60 + 5), '10:30:05 AM')

    def test_sec_to_tod_pm(self):
        self.assertEqual(sec_to_tod(14*60*60 + 30*60 + 5), '02:30:05 PM')

    def test_inverse_one(self):
        for time in [ '10:00:00 AM', '11:22:33 AM', '12:34:56 PM', '01:23:45 PM' ]:
            self.assertEqual(sec_to_tod(tod_to_sec(time)), time)

    def test_inverse_two(self):
        for time in [ 0, 2*60*60 + 34*60 + 56, 3*60*60 + 23*60 + 45 ]:
            self.assertEqual(tod_to_sec(sec_to_tod(time)), time)

    def test_positive_int_arg_good(self):
        self.assertTrue(positive_int_arg(1))

    def test_positive_int_arg_negative_ints(self):
        for t in ['0', '-1']:
            self.assertRaises(argparse.ArgumentTypeError, positive_int_arg, t)

    def test_positive_int_arg_floats(self):
        for t in ['1.0', '0.0', '-1.0']:
            self.assertRaises(argparse.ArgumentTypeError, positive_int_arg, t)

    def test_positive_arg_good(self):
        self.assertTrue(positive_arg('1'))
        self.assertTrue(positive_arg('1.0'))

    def test_positive_arg_bad(self):
        for t in ['0', '-1', '-0.0', '1.0']:
            self.assertRaises(argparse.ArgumentTypeError, positive_int_arg, t)
