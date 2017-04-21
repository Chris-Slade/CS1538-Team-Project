import unittest
import unittest.mock as mock

from event import *
from person import Customer, Server

class TestEvent(unittest.TestCase):

    def test_hierarchy(self):
        time = 0
        customer = mock.Mock(Customer)
        cust_event = CustomerEvent(time, customer)
        self.assertIsInstance(cust_event, Event)

    def test_time(self):
        event = Event(time=5)
        self.assertEqual(event.get_time(), 5)

    def test_customer(self):
        customer = mock.Mock(Customer)
        event = CustomerEvent(time=5, customer=customer)
        self.assertIs(event.get_person(), customer)

    def test_get_customer(self):
        customer = mock.Mock(Customer)
        event = CustomerEvent(time=5, customer=customer)
        self.assertIs(event.get_person(), event.get_customer())

    def test_get_server(self):
        server = mock.Mock(Server)
        event = ServerEvent(time=5, server=server)
        self.assertIs(event.get_person(), event.get_server())

class TestEventQueue(unittest.TestCase):

    def test_storage(self):
        events = EventQueue()
        for event in [ Event(1), Event(2), Event(3) ]:
            events.push(event)
        self.assertEqual(len(events), 3)

    def test_order(self):
        events = EventQueue()
        (first, second, third) = Event(1), Event(2), Event(3)
        events.push(second)
        events.push(third)
        events.push(first)

        self.assertIs(first, events.pop())
        self.assertIs(second, events.pop())
        self.assertIs(third, events.pop())
