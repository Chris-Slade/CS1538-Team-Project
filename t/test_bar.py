import unittest
import unittest.mock as mock

from bar import *
from person import Customer

class TestBar(unittest.TestCase):

    def test_remove_from_empty_bar(self):
        bar = Bar()
        customer = mock.Mock(Customer)
        self.assertRaises(
            CustomerNotPresentError,
            bar.remove_customer,
            customer
        )

    def test_num_seats(self):
        bar = Bar()
        self.assertTrue(hasattr(bar, 'NUM_SEATS'))
        self.assertGreaterEqual(bar.NUM_SEATS, 1)

    def test_add_to_bar(self):
        bar = Bar()
        customer = mock.Mock(Customer)
        self.assertEqual(bar.available_seats(), bar.NUM_SEATS)
        bar.seat_customer(customer)
        self.assertEqual(bar.seated_customers(), 1)
        self.assertEqual(bar.available_seats(), bar.NUM_SEATS - 1)

    def test_add_to_full_bar(self):
        bar = Bar()
        for i in range(0, bar.available_seats()):
            bar.seat_customer(mock.Mock(Customer))
        self.assertRaises(BarFullError, bar.seat_customer, mock.Mock(Customer))
