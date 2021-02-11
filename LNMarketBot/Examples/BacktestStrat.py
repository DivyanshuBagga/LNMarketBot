import time
import talib
from LNMarketBot import Strategy, BacktestBroker, CSVData, Bot


class BacktestStrat(Strategy):

    def init(self):
        self.stopLoss = 0.0
        self.highest = 0.0
        self.drawdown = 0.0
        self.startTime = time.perf_counter()

    def execute(self, datas):
        dtime = datas[0].index
        close = datas[0]["close"]
        low = datas[0]["low"]
        high = datas[0]["high"]

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
        riskAmount = round(self.broker.cashBalance*self.params["RiskPercent"])

        if high[-2] > self.highest:
            self.highest = high[-2]
            self.drawdown = 0.0
        else:
            self.drawdown = self.highest - close[-2]
            if self.drawdown > self.params["TrailPercent"]*self.highest:
                self.broker.closeAllLongs()
                msgTxt = (
                    f'{dtime[-1]}: Trailing stop hit.'
                )
                self.highest = close[-1]
                self.drawdown = 0.0
                self.broker.notifier.notify(msgTxt)

        if ((not closeOverEma) and belowBBand and
            ((close[-1]-self.stopLoss) > self.params["TradeDistance"]*close[-1]
           or low[-1] < self.stopLoss)):
            self.stopLoss = (1-self.params["StopMargin"])*low[-1]
            print(f'Stop Loss set: {self.stopLoss:.2f}')

            leverage = self.params['Leverage']
            quantity = riskAmount // (close[-1] - self.stopLoss)
            if quantity == 0:
                msgTxt = (
                    f'riskAmount {riskAmount} is not sufficient'
                )
            else:
                self.broker.buy(
                    leverage=leverage,
                    quantity=quantity,
                    stoploss=self.stopLoss,
                )
                msgTxt = (
                    f"{dtime[-1]}:"
                    f" Bought {quantity}"
                    f" at price {close[-1]}"
                    f" with liquidation {self.stopLoss:.2f}.\n"
                    f"Balance: {self.broker.balance:.2f}, "
                    f"Cash: {self.broker.cashBalance:.2f}, "
                    f"Borrowed: {self.broker.borrowed:.2f}, "
                    f"Total Position: {self.broker.position}"
                )
            self.broker.notifier.notify(msgTxt)

    def stop(self):
        self.broker.notifier.notify(f"Final Balance: {self.broker.balance:.2f}")
        self.broker.notifier.notify(self.broker.transactions)
        self.broker.notifier.notify(f"Time taken:{time.perf_counter()-self.startTime:.2f}")


broker = BacktestBroker(1.0e05)
broker.notifier.enableStdout()

filename = './BTCPriceData2016Dec.csv'
csvdata = CSVData(filename, 600, datetime='Unnamed: 0',volume='Volume_(BTC)',open_='Open',high='High',low='Low',close='Close')

strategy = BacktestStrat(
    broker=broker,
    BollingerPeriod=20, Deviation=2.0,
    AveragePeriod=240,
    StopMargin=0.02,
    BuyLimit=1.05,
    TradeDistance=0.1,
    RiskPercent=0.02,
    TrailPercent=0.1,
    Leverage=50,
)
strategy.addData(csvdata)

bot = Bot()
bot.addStrategy(strategy)
bot.run()
