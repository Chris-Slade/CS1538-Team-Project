import constants

class Bar(object):
    """Simulates the seats at the bar.

    Not technically needed for the simulation, but this information is useful
    to keep track of for visualization inter alia.
    """
    def __init__(self, num_seats=constants.NUM_BAR_SEATS):
        self.NUM_SEATS = num_seats
        self._seated_customers = 0
        self._seats = [None] * self.NUM_SEATS

    def available_seats(self):
        """Return the number of available seats."""
        return self.NUM_SEATS - self.seated_customers()

    def seated_customers(self):
        return self._seated_customers

    def seat_customer(self, customer):
        """Add a customer to the first available seat at the bar.
        Raises a BarFullError exception if no seats are available.
        """
        if self.available_seats() < 1:
            raise BarFullError("Can't seat customer when bar is full")
        seated_customer = False
        for i, seat in enumerate(self._seats):
            if seat is None:
                self._seats[i] = customer
                self._seated_customers += 1
                seated_customer = True
                break
        assert seated_customer

    def remove_customer(self, customer):
        for i, seat in enumerate(self._seats):
            if customer == self._seats[i]:
                self._seats[i] = None
                self._seated_customers -= 1
                return customer
        raise CustomerNotPresentError('%s is not present at bar' % customer)

    def __str__(self):
        return self._seats.__str__()

class BarFullError(Exception):
    pass

class CustomerNotPresentError(Exception):
    pass
