import pandas as pd
import random
from collections import deque
from .Broker import Broker
from .Order import Order


class BacktestBroker(Broker):

    def __init__(self, balance, maxLeverage=1, interest=0, commission=0.001,
                 liveTrading=False, symbol='BTC'):
        self._balance = balance
        self._cashBalance = balance
        self._borrowed = 0
        self._borrowedShares = 0
        self.maxLeverage = maxLeverage
        self.interest = interest
        self.commission = commission
        self.liveTrading = liveTrading
        self.symbol = symbol
        self.price = None
        self.transactions = pd.DataFrame(columns=[
            'amount',
            'price',
            'symbol',
        ], index=pd.to_datetime([]))
        self.book = pd.DataFrame(columns=[
            'balance',
            'cashBalance',
            'borrowed',
            'borrowedShares',
            symbol,
            'returns',
        ], index=pd.to_datetime([]))
        self.orders = deque()
        super().__init__()

    @property
    def balance(self):
        if self.price is not None:
            return (self.cashBalance
                    + (self.position) * self.price['close'][0]
                    )
        else:
            return self.cashBalance

    @property
    def cashBalance(self):
        return self._cashBalance - self.borrowed

    @property
    def position(self):
        return self.transactions['amount'].sum()

    @property
    def borrowed(self):
        return self._borrowed

    @property
    def borrowedShares(self):
        return self._borrowedShares

    def buy(self, strategy, quantity, leverage, stoploss=None, takeprofit=None,
            limit=None):
        self.orders.append(Order(
            Type='buy',
            Quantity=quantity,
            Leverage=leverage,
            Stoploss=stoploss,
            Takeprofit=takeprofit,
            Limit=limit,
            Parent=None,
            Strategy=strategy,
        ))

    def sell(self, strategy, quantity, leverage, stoploss=None, takeprofit=None,
             limit=None):
        self.orders.append(Order(
            Type='sell',
            Quantity=quantity,
            Leverage=leverage,
            Stoploss=stoploss,
            Takeprofit=takeprofit,
            Limit=limit,
            Parent=None,
            Strategy=strategy,            
        ))

    def closeAllLongs(self, strategy):
        if self.position > 0:
            self.orders.append(Order(
                Type='sell',
                Quantity=self.position,
                Leverage=1,
                Stoploss=None,
                Takeprofit=None,
                Limit=None,
                Parent=None,
                Strategy=strategy,
            ))

    def closeAllShorts(self, strategy):
        if self.position < 0:
            self.orders.append(Order(
                Type='buy',
                Quantity=(-self.position),
                Leverage=1,
                Stoploss=None,
                Takeprofit=None,
                Limit=None,
                Parent=None,
                Strategy=strategy,
            ))

    def calculateShareDebt(self, freeShares):
        if self.borrowedShares >= freeShares:
            self._borrowedShares -= freeShares
        else:
            self._borrowedShares = 0

    def calculateDebt(self, freeCapital):
        if self.borrowed >= freeCapital:
            self._borrowed -= freeCapital
        else:
            self._cashBalance += (freeCapital - self.borrowed)
            self._borrowed = 0

    def processBuy(self, order, price):
        assert(order.Leverage > 0)
        assert(order.Type == 'buy')

        cost = (1+self.commission)*order.Quantity*price/order.Leverage
        if cost > self.cashBalance:
            print(f"Balance {self.cashBalance:.2f} not enough"
                             f" to cover cost {cost:.2f}")

        # Add transaction
        if self.price.index[0] in self.transactions.index:
            self.transactions.loc[self.price.index[0]] = [
                (self.transactions.loc[self.price.index[0]].amount
                 + order.Quantity),
                price,
                self.symbol,
            ]
        else:
            self.transactions.loc[self.price.index[0]] = [
                order.Quantity,
                price,
                self.symbol,
            ]
        self.transactions = self.transactions.sort_index()
        self._cashBalance = self._cashBalance - cost
        self._borrowed += cost*order.Leverage - cost
        self.calculateShareDebt(order.Quantity)
        order.Strategy.notifyOrder(order, price)

    def processSell(self, order, price):
        assert(order.Leverage > 0)
        assert(order.Type == 'sell')

        netQuantity = self.position - order.Quantity/order.Leverage + self.borrowedShares
        value = abs(netQuantity) * price
        if self.position > 0:
            balance = self.cashBalance + self.position * price
        else:
            balance = self.cashBalance
        if netQuantity < 0 and value > balance * order.Leverage:
            print(f"Cash Balance {self.cashBalance:.2f} not enough"
                  f" to borrow {order.Quantity} shares"
                  f" at leverage {order.Leverage:.2f}")
                
        freeCapital = (1-self.commission) * order.Quantity * price

        # Add transaction
        if self.price.index[0] in self.transactions.index:
            self.transactions.loc[self.price.index[0]] = [
                (self.transactions.loc[self.price.index[0]].amount
                 - order.Quantity),
                price,
                self.symbol,
            ]
        else:
            self.transactions.loc[self.price.index[0]] = [
                - order.Quantity,
                price,
                self.symbol,
            ]
        self.transactions = self.transactions.sort_index()
        self._borrowedShares = order.Quantity - order.Quantity//order.Leverage
        self.calculateDebt(freeCapital)
        order.Strategy.notifyOrder(order, price)

    def processData(self, priceData):
        last = priceData[0].tail(1)
        self.price = last
        if self.balance <= 0:
            raise ValueError(
                f"{self.price.index[0]}: Account liquidated\n"
                f"Borrowed: {self.borrowed:.2f}\n"
                f"cash: {self.cashBalance:.2f}\n"
                f"Position: {self.position}, Price: {self.price['close'][0]}"
            )
        if (last.index[0].second == 0 and
            last.index[0].minute == 0 and
            last.index[0].hour == 0):
            self._cashBalance -= self.interest*self.borrowed
            try:
                self.book.loc[last.index[0]] = [
                    self.balance,
                    self.cashBalance,
                    self.borrowed,
                    self.borrowedShares,
                    self.position,
                    (self.balance - self.book.tail(1)['balance'][0])/self.balance,
                ]
            except IndexError:
                self.book.loc[last.index[0]] = [
                    self.balance,
                    self.cashBalance,
                    self.borrowed,
                    self.borrowedShares,
                    self.position,
                    0.0,
                ]

        leftOrders = deque()
        while self.orders:
            order = self.orders.popleft()
            if order.Limit is None:
                # Oder executed at random price between high and low
                weight = (random.randint(0, 100)/100)
                diff = last['high'][0]-last['low'][0]
                price = last['low'][0] + weight*diff
                if order.Type == 'buy':
                    self.processBuy(order, price)
                else:
                    self.processSell(order, price)

            else:
                if order.Type == 'buy':
                    if order.Limit > last['low'][0]:
                        self.processBuy(order, order.Limit)
                    else:
                        leftOrders.append(order)
                if order.Type == 'sell':
                    if order.Limit < last['high'][0]:
                        self.processSell(order, order.Limit)
                    else:
                        leftOrders.append(order)
        self.orders = leftOrders


