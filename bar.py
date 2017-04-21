import constants

class Bar(object):
    """Simulates the seats at the bar.

    Not technically needed for the simulation, but this information is useful
    to keep track of for visualization inter alia.
    """
    NUM_SEATS = constants.NUM_BAR_SEATS

    def __init__(self):
        self._seated_customers = 0
        self._seats = [None] * Bar.NUM_SEATS

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
        for i, seat in enumerate(self._seats):
            if seat is None:
                self._seats[i] = customer
                self._seated_customers += 1
                break

    def remove_customer(self, customer):
        try:
            removed = self._seats.remove(customer)
        except ValueError:
            raise CustomerNotPresentError('Customer is not present at bar')
        self._seated_customers -= 1
        return removed

class BarFullError(Exception):
    pass

class CustomerNotPresentError(Exception):
    pass
