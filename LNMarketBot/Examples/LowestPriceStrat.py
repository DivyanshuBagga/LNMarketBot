import talib
from LNMarketBot import Strategy


class LowestPriceStrat(Strategy):

    def init(self):
        self.stopLoss = 0.0
        self.highest = 0.0
        self.drawdown = 0.0
        self.openCount = len(self.broker.openPositions)

    def execute(self, ohlc):
        dtime = ohlc.index
        close = ohlc["close"]
        low = ohlc["low"]
        high = ohlc["high"]
        open = ohlc["open"]

        upper, middle, lower = talib.BBANDS(
            close,
            self.params["BollingerPeriod"],
            self.params["Deviation"],
            self.params["Deviation"]
        )
        ema = talib.EMA(close, self.params["AveragePeriod"])
        closeOverEma = close[-1] > ema[-1]
        belowBBand = low[-1] < lower[-1]

        assert(self.broker is not None)
        riskAmount = min(round(self.broker.balance*self.params["RiskPercent"]),
                         self.params["CashLimit"]-self.broker.marginWithheld)

        if high[-2] > self.highest:
            self.highest = high[-2]
            self.drawdown = 0.0
        else:
            self.drawdown = self.highest - close[-2]
            if self.drawdown > self.params["TrailPercent"]*self.highest:
                pl = self.broker.closeAllLongs()
                msgTxt = f'{dtime[-1].isoformat()}: Trailing stop hit.'
                f'Exited all position for profit(loss) of {pl:.2f}'
                self.highest = close[-2]
                self.drawdown = 0.0
                self.openCount = len(self.broker.openPositions)
                self.broker.notifier.notify(msgTxt)

        print(f"{dtime[-1]}: Close: {close[-1]:.2f},"
              f" BBand Bot: {lower[-1]:.2f}, EMA: {ema[-1]:.2f}")

        if (self.openCount < 50 and (not closeOverEma) and belowBBand and
            ((close[-2]-self.stopLoss) > self.params["TradeDistance"]*close[-2]
           or low[-2] < self.stopLoss)):
            self.stopLoss = (1-self.params["StopMargin"])*low[-2]
            print(f'Stop Loss set: {self.stopLoss}')

            leverage = min(
                round((0.9*close[-1])/(close[-1] - self.stopLoss)),
                50,
            )
            assert(self.stoploss != 0 and close[-1] != 0)
            marginReq = round(1.0e08*(1/self.stopLoss - 1/close[-1]))
            quantity = riskAmount // marginReq
            if quantity == 0:
                msgTxt = f'riskAmount {riskAmount} is not sufficient'
                f'for margin {marginReq}'
            else:
                buyInfo = self.broker.buy(
                    leverage=leverage,
                    quantity=quantity,
                )['position']
                self.openCount = len(self.broker.openPositions)
                msgTxt = f"{buyInfo['market_filled_ts']}:"
                f" Bought {buyInfo['quantity']} at price {buyInfo['price']}"
                f" with liquidation {buyInfo['liquidation']}.\n"
                f"Balance: {self.broker.balance}"
            self.broker.notifier.notify(msgTxt)
