# LNMarkets Trading Bot

A trading bot for [LNMarkets](https://lnmarkets.com/), using the [LNMarkets API](https://pypi.org/project/LNMarkets/) in Python.

To install: `pip install LNMarketBot`

An abstract class `LNMarketBot.Strategy` is provided, which must be extended with implementation of `LNMarketBot.Strategy.init()`, `LNMarketBot.Strategy.execute()`, and `LNMarketBot.Strategy.stop()` methods. The `init()` method will be called only once, before the bot starts processing price information, while `execute()` is called repetedly, for every new price bar that bot recieves. Any parameters required by the strategy, can be passed during instantiation, and will be accessible using `LNMarketBot.Strategy.params` dictionary. Example strategies are provided in LNMarketBot/Examples/ on github.

The price information is obtained from Kraken, using [Pykrakenapi](https://github.com/dominiktraxl/pykrakenapi), as the methods for same are currently not working for LNMarkets API. This may result in price discrepancy between strategy and broker execution. The price bars are of 1 minute duration, and at present, only supplied for last 12 hours. You can also provide csv files containing price information for backtesting (see examples). A strategy can consume data from multiple data feeds, and bot can process multiple strategies simultaneously.

 Bot interacts with LNMarkets through `LNMarketBot.LNMBroker` class, which provides methods for buying/selling, as well as properties for viewing opne/closed positions, balance, etc. If backtesting, the strategy connects to `LNMarketBot.BacktestBroker` class instead.
 
 You can enable Telegram or Pushover notifications through `LNMarketBot.Notifier`, which provides methods enableTelegram(chatID, token) and enablePushover(userkey, APIkey) for the same. A notifier instance is added to broker on instantiation and access via `broker.notifier` and all position updates through broker will automatically be notified. If you want to disable the automatic notification, instantiate broker with `silent=False`.

Example Usage:
```python
import LNMarketBot

LNMToken = '<YOUR TOKEN>'
broker = LNMarketBot.Broker(LNMToken, <Starting Balance>)
telegramToken = '<Telegram Bot Token>'
chatId = <Your Chat Id with Telegram Bot>
broker.notifier.enableTelegram(chatID = chatId, token = telegramToken)

#LowestPriceStrat is provided in LNMarketBot/Examples/ on git
strategy = LowestPriceStrat(
    broker=broker,
    BollingerPeriod=20, Deviation=2.0,
    AveragePeriod=240,
    StopMargin=0.02,
    BuyLimit=1.05,
    TradeDistance=0.1,
    RiskPercent=0.01,
    TrailPercent=0.1,
    CashLimit=1.0e06,
)

bot = LNMarketBot.Bot()
bot.addStrategy(strategy)
bot.run()
```

Note:
* LNMarket token needs only 'positions' scope. This ensures leaking it cannot result in loss of funds through withdrawal.
* This project is under development and not well tested. You are advised to review the code if you plan to use it for trading.
* The author is not responsible for any loss that may result from use of this project.
