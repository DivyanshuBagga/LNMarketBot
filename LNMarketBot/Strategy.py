from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):

    def __init__(self, broker=None, **params):
        self.params = params
        self.broker = broker
        self.init()

    @abstractmethod
    def init(self):
        pass

    @abstractmethod
    def execute(self):
        pass

    def addBroker(self, broker):
        self.broker = broker
