from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):

    def __init__(self, broker=None, **params):
        self.params = params
        self.broker = broker
        self.datas = []
        self.init()

    @abstractmethod
    def init(self):
        """
        This method is called only once, before any price bar is recieved.
        """
        pass

    @abstractmethod
    def execute(self):
        """
        This method is called for every new bar recieved.
        """
        pass

    @abstractmethod
    def stop(self):
        """
        This method is called only once, when there is no new price bars left.
        """
        pass

    def addBroker(self, broker):
        self.broker = broker

    def addData(self, data):
        self.datas.append(data)
