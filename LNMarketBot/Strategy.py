import time
import pandas as pd
from abc import ABCMeta, abstractmethod


class Strategy(metaclass=ABCMeta):

    def __init__(self, broker=None, **params):
        self.params = params
        self.broker = broker
        self.datas = []
        self.dataIndex = []

        self.highest = 0.0
        self.drawdown = 0.0
        self.maxdrawdown = 0.0
        if broker is not None:
            self.initialCapital = broker.balance
        self.startTime = time.perf_counter()
        self.position = 0
        self.orderBook = pd.DataFrame(columns=[
            'Type',
            'Limit',
            'Quantity',
            'Leverage',
            'Stoploss',
            'Takeprofit',
            'Parent',
            'Strategy',
            'StopExecuted',
            'ProfitExecuted',
        ], index=pd.Series([]))

        self.init()

    @abstractmethod
    def init(self):
        """
        This method is called only once, before any price bar is recieved.
        """
        pass

    @abstractmethod
    def execute(self, datas):
        """
        This method is called for every new bar recieved.
        """
        pass

    def processData(self, datas):
        self.computeDrawdown()
        last = datas[0].tail(1)
        for index, order in self.orderBook.loc[(lambda df: (df['Stoploss'].notnull())
                                                & (df['StopExecuted'] == False)
                                                & (df['ProfitExecuted'] == False))].iterrows():
            if order.Type == 'buy' and order.Stoploss > last['low'][0]:
                self.broker.sell(
                    quantity=order.Quantity,
                    leverage=order.Leverage,
                    strategy=order.Strategy
                    )
                self.orderBook.at[index, 'StopExecuted'] = True
            elif (order.Type == 'sell' and
                  order.Stoploss < last['high'][0]):
                self.broker.buy(
                    quantity=order.Quantity,
                    leverage=order.Leverage,
                    strategy=order.Strategy
                    )
                self.orderBook.at[index, 'StopExecuted'] = True
        for index, order in self.orderBook.loc[(lambda df: (df['Takeprofit'].notnull())
                                                & (df['StopExecuted'] == False)
                                                & (df['ProfitExecuted'] == False))].iterrows():
            if order.Type == 'buy':
                if order.Takeprofit < last['high'][0]:
                    self.broker.sell(
                        quantity=order.Quantity,
                        leverage=order.Leverage,
                        strategy=order.Strategy
                    )
                    self.orderBook.at[index, 'ProfitExecuted'] = True
            if order.Type == 'sell':
                if order.Takeprofit > last['low'][0]:
                    self.broker.buy(
                        quantity=order.Quantity,
                        leverage=order.Leverage,
                        strategy=order.Strategy
                    )
                    self.orderBook.at[index, 'ProfitExecuted'] = True
        self.execute(datas)

    def computeDrawdown(self):
        balance = self.broker.balance
        if balance > self.highest:
            self.highest = balance
            self.drawdown = 0
        else:
            self.drawdown = self.highest - balance
            if balance != 0 and self.drawdown/balance > self.maxdrawdown:
                self.maxdrawdown = self.drawdown/balance

    def notifyOrder(self, order, price):
        """
        This method is called whenever the order provided by strategy is executed.
        """
        self.orderBook = self.orderBook.append({
            'Type': order.Type,
            'Limit': order.Limit,
            'Quantity': order.Quantity,
            'Leverage': order.Leverage,
            'Stoploss': order.Stoploss,
            'Takeprofit': order.Takeprofit,
            'Parent': order.Parent,
            'Strategy': order.Strategy,
            'StopExecuted': False,
            'ProfitExecuted': False,
        }, ignore_index=True)

        if order.Type == 'buy':
            self.position += order.Quantity
        elif order.Type == 'sell':
            self.position -= order.Quantity

        self.broker.notifier.notify(f"{price.index[0]}: {order.Type} "
                                    f" Executed at price {price['close'][0]:.2f}"
                                    f" Quantity: {order.Quantity}"
        )

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
