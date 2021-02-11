from abc import ABCMeta, abstractmethod
from .Notifier import Notifier


class Broker(metaclass=ABCMeta):

    def __init__(self, silent=False):
        self.notifier = Notifier(silent)

    @abstractmethod
    def processData(self, priceData):
        """
        This method is called every time a new price bar is recieved.
        Input priceData is list of dataframes containing price information.
        """
        pass

    @property
    @abstractmethod
    def balance(self):
        pass

    @property
    @abstractmethod
    def cashBalance(self):
        pass

    @property
    @abstractmethod
    def position(self):
        pass

    @abstractmethod
    def buy(self, quantity, leverage, stoploss=None, takeprofit=None,
            limit=None):
        pass

    @abstractmethod
    def sell(self, quantity, leverage, stoploss=None, takeprofit=None,
             limit=None):
        pass

    @abstractmethod
    def closeAllLongs(self):
        pass

    @abstractmethod
    def closeAllShorts(self):
        pass
