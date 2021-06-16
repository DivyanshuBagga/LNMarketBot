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
        self.datas = []
        self.dataIndex = 0

    def run(self):
        priceGens = []
        for data in self.datas:
            priceGens.append(data.dataGenerator())
        loop = True
        eventLoop = asyncio.get_event_loop()
        while loop:
            prices = []
            try:
                for gen in priceGens:
                    prices.append(gen.__anext__())
                prices = eventLoop.run_until_complete(asyncio.gather(*prices))
            except StopAsyncIteration:
                break
            for strategy in self.strategy:
                stratPrices = []
                for index in strategy.dataIndex:
                    stratPrices.append(prices[index])
                try:
                    strategy.broker.processData(stratPrices)
                    strategy.processData(stratPrices)
                except ValueError as VErr:
                    strategy.broker.notifier.notify(str(VErr))
                    loop = False
                    break
                except Exception as exception:
                    strategy.broker.notifier.notify(str(exception))
                    raise exception
            sys.stdout.flush()
        #eventLoop.close()
        for strategy in self.strategy:
            strategy.stop()

    def addStrategy(self, strategy):
        if strategy.broker is None:
            raise ValueError("Add Broker to Strategy first")
        self.strategy.append(strategy)
        for data in strategy.datas:
            try:
                strategy.dataIndex.append(self.datas.index(data))
            except ValueError:
                self.datas.append(data)
                strategy.dataIndex.append(self.dataIndex)
                self.dataIndex += 1
