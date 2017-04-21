"""Unit tests for the customer class."""

import unittest

import person
from person import Customer

class TestCustomer(unittest.TestCase):

    def test_init(self):
        customer = Customer() # Customer who arrived after 5 minutes
        self.assertTrue(True, "Constructor shouldn't throw exceptions")

# End of TestCustomer

if __name__ == '__main__':
    unittest.main()
