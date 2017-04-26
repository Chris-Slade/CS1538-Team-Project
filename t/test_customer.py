"""Unit tests for the customer class."""

import unittest

import person
from person import Customer

class TestCustomer(unittest.TestCase):

    def test_init(self):
        customer = Customer(arrival_time=5)
        self.assertTrue(True, "Constructor shouldn't throw exceptions")

    def test_drinks_wanted(self):
        customer = Customer(arrival_time=5)
        self.assertIsNotNone(customer.drinks_wanted())

    def test_drink(self):
        customer = Customer(arrival_time=5)
        drinks_wanted = customer.drinks_wanted()
        customer.drink()
        self.assertEqual(customer.drinks_wanted(), drinks_wanted - 1)

# End of TestCustomer

if __name__ == '__main__':
    unittest.main()
