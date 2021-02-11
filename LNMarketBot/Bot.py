import sys
import asyncio


def background(f):
    def wrapped(*args, **kwargs):
        return asyncio.get_event_loop().run_in_executor(None, f,
                                                        *args, **kwargs)

    return wrapped


class Bot:

    def __init__(self):
        self.strategy = []

    def run(self):
        for strat in self.strategy:
            self.runStrategy(strat)

    # @background
    def runStrategy(self, strategy):
        assert(strategy.datas)
        priceGens = []
        for data in strategy.datas:
            priceGens.append(data.dataGenerator())
        while True:
            prices = []
            try:
                for gen in priceGens:
                    prices.append(next(gen))
            except StopIteration:
                break
            try:
                strategy.broker.processData(prices)
                strategy.execute(prices)
            except ValueError as VErr:
                strategy.broker.notifier.notify(str(VErr))
                break
            except Exception as exception:
                strategy.broker.notifier.notify(str(exception))
                raise exception
            sys.stdout.flush()
        strategy.stop()

    def addStrategy(self, strategy):
        if strategy.broker is None:
            raise ValueError("Add Broker to Strategy first")
        self.strategy.append(strategy)
