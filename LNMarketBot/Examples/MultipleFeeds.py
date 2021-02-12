import time
import talib
import datetime
from LNMarketBot import Strategy, BacktestBroker, CSVData, Bot


class MultipleFeedStrat(Strategy):

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
        close1 = datas[1]["close"]
        close2 = datas[2]["close"]

        upper, middle, lower = talib.BBANDS(
            close,
            self.params["BollingerPeriod"],
            self.params["Deviation"],
            self.params["Deviation"]
        )
        belowBBand = low[-1] < lower[-1]
        ema1 = talib.EMA(close1, self.params["AveragePeriod"])
        closeBelowEma1 = close[-1] < ema1[-1]
        ema2 = talib.EMA(close2, self.params["TrendPeriod"])
        closeOverEma2 = close[-1] > ema2[-1]

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

        if (belowBBand and closeBelowEma1 and closeOverEma2 and
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


if __name__ == '__main__':
    broker = BacktestBroker(1.0e05)
    broker.notifier.enableStdout()

    startDate = datetime.datetime(2016, 12, 1, 1, 0, 0)
    endDate = datetime.datetime(2016, 12, 31, 23, 59, 0)
    dirname = '<Direcory Path>'
    # window 50 is sufficient to compute 20 minute bollinger bands.
    filename1 = 'BTCPriceData2016.csv'
    csvdata1 = CSVData(
        dirname + filename1,
        window=datetime.timedelta(minutes=50),
        datetime='Unnamed: 0',
        start=startDate,
        end=endDate,
    )

    # window 20 is sufficient to compute 12 hour moving average.
    filename2 = 'BTCPriceData2012-2020Hourly.csv'
    csvdata2 = CSVData(
        dirname + filename2,
        window=datetime.timedelta(hours=20),
        datetime='Unnamed: 0',
        start=startDate,
        end=endDate,
    )

    # window 150 is sufficient to compute 100 day moving average.
    filename3 = 'BTCPriceData2012-2020Daily.csv'
    csvdata3 = CSVData(
        dirname + filename3,
        window=datetime.timedelta(days=150),
        datetime='Unnamed: 0',
        start=startDate,
        end=endDate,
    )

    strategy = MultipleFeedStrat(
        broker=broker,
        BollingerPeriod=20, Deviation=2.0,
        AveragePeriod=12,
        TrendPeriod=100,
        StopMargin=0.02,
        BuyLimit=1.05,
        TradeDistance=0.1,
        RiskPercent=0.02,
        TrailPercent=0.1,
        Leverage=50,
    )
    strategy.addData(csvdata1)
    strategy.addData(csvdata2)
    strategy.addData(csvdata3)

    bot = Bot()
    bot.addStrategy(strategy)
    bot.run()
