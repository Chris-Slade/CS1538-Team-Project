from constants import DRINK_TIME_LAMBDA


class Server(object):

    def __init__(self):
        self._skill = Server.get_skill()

    @staticmethod
    def get_skill():
        return 1

    @staticmethod
    def get_seating_time():
        return int(abs(round(numpy.random.exponential(1 / DRINK_TIME_LAMBDA))))
