from .Broker import Broker
from .Notifier import addMessage
from .Order import Order
from LNMarkets import Positions


class LNMBroker(Broker):

    def __init__(self, token, initialBalance, silent=False):
        self.token = token
        self.initialBalance = initialBalance
        self._position = 0
        super().__init__()

    @staticmethod
    def calculateProfit(positions):
        totalProfit = 0.0
        for position in positions:
            totalProfit += float(position['pl'])

        return totalProfit

    @staticmethod
    def calculateMargin(positions):
        totalMargin = 0.0
        for position in positions:
            totalMargin += float(position['margin'])
        return totalMargin

    @property
    def position(self):
        return self._position

    @position.setter
    def position(self, position):
        self._position = position

    @property
    def openPositions(self):
        return Positions.getPositions(self.token, "open")

    @property
    def closedPositions(self):
        return Positions.getPositions(self.token, "closed")

    @property
    def unrealizedProfit(self):
        return self.calculateProfit(self.openPositions)

    @property
    def realizedProfit(self):
        return self.calculateProfit(self.closedPositions)

    @property
    def balance(self):
        return self.cashBalance + self.unrealizedProfit

    @property
    def cashBalance(self):
        return self.realizedProfit + self.initialBalance

    @property
    def marginWithheld(self):
        return self.calculateMargin(self.openPositions)

    @addMessage
    def buy(self, strategy, leverage, quantity=None, margin=None, stoploss=None, takeprofit=None,
            limit=None):
        assert(margin is not None or quantity is not None)
        if limit is None:
            positionData = Positions.buy(
                token=self.token,
                leverage=leverage,
                quantity=quantity,
                margin=margin,
                stoploss=stoploss,
                takeprofit=takeprofit,
            )
        else:
            positionData = Positions.limitBuy(
                token=self.token,
                leverage=leverage,
                price=limit,
                quantity=quantity,
                stoploss=stoploss,
                takeprofit=takeprofit,
            )
        strategy.notifyOrder(Order(
                    Type='buy',
                    Quantity=positionData['position']['quantity'],
                    Leverage=leverage,
                    Stoploss=stoploss,
                    Takeprofit=takeprofit,
                    Limit=limit,
                    Parent=None,
                    Strategy=strategy,
                ), positionData['position']['price'])
        return positionData

    @addMessage
    def sell(self, strategy, leverage, quantity=None, margin=None, stoploss=None, takeprofit=None,
             limit=None):
        assert(margin is not None or quantity is not None)
        if limit is None:
            positionData = Positions.sell(
                token=self.token,
                leverage=leverage,
                quantity=quantity,
                margin=margin,
                stoploss=stoploss,
                takeprofit=takeprofit,
            )
        else:
            positionData = Positions.limitSell(
                token=self.token,
                leverage=leverage,
                price=limit,
                quantity=quantity,
                margin=margin,
                stoploss=stoploss,
                takeprofit=takeprofit,
            )
        strategy.notifyOrder(Order(
                    Type='sell',
                    Quantity=positionData['position']['quantity'],
                    Leverage=leverage,
                    Stoploss=stoploss,
                    Takeprofit=takeprofit,
                    Limit=limit,
                    Parent=None,
                    Strategy=strategy,
                ), positionData['position']['price'])
        return positionData

    @addMessage
    def updateProfit(self, pid, price):
        return Positions.updatePosition(
            token=self.token,
            pid=pid,
            type_='takeprofit',
            value=price,
            )

    @addMessage
    def updateStoploss(self, pid, price):
        return Positions.updatePosition(
            token=self.token,
            pid=pid,
            type_='stoploss',
            value=price,
            )

    @addMessage
    def closePosition(self, pid):
        return Positions.closePosition(self.token, pid)

    @addMessage
    def closeAllLongs(self):
        return Positions.closeAllLongs(self.token)

    @addMessage
    def closeAllShorts(self):
        return Positions.closeAllShorts(self.token)

    @addMessage
    def cancelPosition(self, pid):
        return Positions.cancelPosition(self.token, pid)

    @addMessage
    def addMargin(self, pid, amount):
        return Positions.addMargin(self.token, pid, amount)

    @addMessage
    def cashin(self, pid, amount):
        return Positions.cashin(self.token, pid, amount)

    def isOpen(self, pid):
        return Positions.isOpen(self.token, pid)

    def processData(self, priceData):
        pass
