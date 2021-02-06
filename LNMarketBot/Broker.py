from LNMarkets import Positions
from .Notifier import Notifier, addMessage


class Broker:

    def __init__(self, token, initialBalance, silent=False):
        self.token = token
        self.initialBalance = initialBalance
        self.notifier = Notifier(silent)

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
    def openPositions(self):
        return Positions.getPositions(self.token, "open")['open']

    @property
    def closedPositions(self):
        return Positions.getPositions(self.token, "closed")['closed']

    @property
    def unrealizedProfit(self):
        return self.calculateProfit(self.openPositions)

    @property
    def realizedProfit(self):
        return self.calculateProfit(self.closedPositions)

    @property
    def balance(self):
        return self.realizedProfit + self.initialBalance

    @property
    def marginWithheld(self):
        return self.calculateMargin(self.openPositions)

    @addMessage
    def buy(self, leverage, margin=None, quantity=None, stoploss=None,
            takeprofit=None):
        return Positions.buy(
            token=self.token,
            leverage=leverage,
            margin=margin,
            quantity=quantity,
            stoploss=stoploss,
            takeprofit=takeprofit,
        )

    @addMessage
    def limitBuy(self, leverage, price, margin=None, quantity=None,
                 stoploss=None, takeprofit=None):
        return Positions.limitBuy(
            token=self.token,
            leverage=leverage,
            price=price,
            margin=margin,
            quantity=quantity,
            stoploss=stoploss,
            takeprofit=takeprofit,
        )

    @addMessage
    def sell(self, leverage, margin=None, quantity=None, stoploss=None,
             takeprofit=None):
        return Positions.sell(
            token=self.token,
            leverage=leverage,
            margin=margin,
            quantity=quantity,
            stoploss=stoploss,
            takeprofit=takeprofit,
        )

    @addMessage
    def limitSell(self, leverage, price, margin=None, quantity=None,
                  stoploss=None, takeprofit=None):
        return Positions.limitSell(
            token=self.token,
            leverage=leverage,
            price=price,
            margin=margin,
            quantity=quantity,
            stoploss=stoploss,
            takeprofit=takeprofit,
        )

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
