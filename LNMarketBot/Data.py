from abc import ABCMeta, abstractmethod


class Data(metaclass=ABCMeta):

    def __init__(self):
        pass

    @abstractmethod
    def dataGenerator(self):
        """
        Genrtator which yields datetime index dataframe containing
        open, high, low, and close prices with volume
        for each new price bar recieved.
        """
        pass
