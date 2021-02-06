import time
import sys
import krakenex
from pykrakenapi import KrakenAPI


class Bot:

    def __init__(self, useKraken=True, interval=1):
        self.useKraken = useKraken
        self.KAPI = KrakenAPI(krakenex.API())
        self.ohlc, self.since = self.KAPI.get_ohlc_data(
            "BTCUSD",
            interval=interval,
            since=None,
            ascending=True,
        )
        self.strategy = []

    def run(self, interval=1):
        wait = 60
        maxRows = 2880
        blockSize = 1440
        retry = 0
        while retry < 10:
            try:
                ohlcnew, self.since = self.KAPI.get_ohlc_data(
                    "BTCUSD",
                    interval=interval,
                    since=self.since,
                    ascending=True,
                )
            except [TimeoutError, ConnectionError]:
                time.sleep(wait)
                retry += 1
                continue

            # Remove the last enty as it is unconfirmed
            self.ohlc.drop(self.ohlc.tail(1).index, inplace=True)
            self.ohlc = self.ohlc.append(ohlcnew)
            if len(self.ohlc) >= maxRows:
                self.ohlc.drop(self.ohlc.head(blockSize).index,
                               inplace=True)
                
            if self.strategy:
                for strat in self.strategy:
                    strat.execute(self.ohlc)
            else:
                raise ValueError("Add Strategy to run Bot")

            sys.stdout.flush()
            time.sleep(interval*wait)

    def addStrategy(self, strategy):
        if strategy.broker is None:
            raise ValueError("Add Broker to Strategy first")
        self.strategy.append(strategy)
