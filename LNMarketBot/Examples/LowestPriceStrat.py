import talib
from LNMarketBot import Strategy, LNMBroker, KrakenData, Bot


class LowestPriceStrat(Strategy):

    def init(self):
        self.stopLoss = 0.0
        self.highest = 0.0
        self.drawdown = 0.0
        self.openCount = len(self.broker.openPositions)

    def execute(self, datas):
        dtime = datas[0].index
        close = datas[0]["close"]
        low = datas[0]["low"]
        high = datas[0]["high"]
        open_ = datas[0]["open"]

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
        riskAmount = min(round(self.broker.cashBalance*self.params["RiskPercent"]),
                         self.params["CashLimit"]-self.broker.marginWithheld)

        if high[-2] > self.highest:
            self.highest = high[-2]
            self.drawdown = 0.0
        else:
            self.drawdown = self.highest - close[-2]
            if self.drawdown > self.params["TrailPercent"]*self.highest:
                pl = self.broker.closeAllLongs()
                msgTxt = (
                    f'{dtime[-1].isoformat()}: Trailing stop hit.'
                    f'Exited all position for profit(loss) of {pl:.2f}'
                )
                self.highest = close[-2]
                self.drawdown = 0.0
                self.openCount = len(self.broker.openPositions)
                self.broker.notifier.notify(msgTxt)

        print(f"{dtime[-1]}: Close: {close[-1]:.2f},"
              f" BBand Bot: {lower[-1]:.2f}, EMA: {ema[-1]:.2f}")

        if (self.openCount < 50 and (not closeOverEma) and belowBBand and
            ((close[-1]-self.stopLoss) > self.params["TradeDistance"]*close[-1]
           or low[-1] < self.stopLoss)):
            self.stopLoss = (1-self.params["StopMargin"])*low[-1]
            print(f'Stop Loss set: {self.stopLoss}')

            leverage = min(
                round((0.9*close[-1])/(close[-1] - self.stopLoss)),
                50,
            )
            assert(self.stopLoss != 0 and close[-1] != 0)
            marginReq = round(1.0e08*(1/self.stopLoss - 1/close[-1]))
            quantity = riskAmount // marginReq
            if quantity == 0:
                msgTxt = (
                    f'riskAmount {riskAmount} is not sufficient'
                    f'for margin {marginReq}'
                )
            else:
                buyInfo = self.broker.buy(
                    leverage=leverage,
                    quantity=quantity,
                )['position']
                self.openCount = len(self.broker.openPositions)
                msgTxt = (
                    f"{buyInfo['market_filled_ts']}:"
                    f" Bought {buyInfo['quantity']}"
                    f" at price {buyInfo['price']}"
                    f" with liquidation {buyInfo['liquidation']}.\n"
                    f"cash Balance: {self.broker.cashBalance}"
                )
            self.broker.notifier.notify(msgTxt)

    def stop(self):
        self.broker.notifier.notify(f"Final Balance: {self.broker.balance:.2f}")

LNMToken = '<LNMarkets API token with position scope>'
broker = LNMBroker(LNMToken, <initial cash>)
telegramToken = '<Telegram Token>'
chatId = <chat id>
broker.notifier.enableTelegram(chatID=chatId, token=telegramToken)

strategy = LowestPriceStrat(
    broker=broker,
    BollingerPeriod=20, Deviation=2.0,
    AveragePeriod=240,
    StopMargin=0.02,
    BuyLimit=1.05,
    TradeDistance=0.1,
    RiskPercent=0.02,
    TrailPercent=0.1,
    CashLimit=1.0e06,
)
strategy.addData(KrakenData())

bot = Bot()
bot.addStrategy(strategy)
bot.run()
