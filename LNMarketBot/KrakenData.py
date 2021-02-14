import asyncio
import time
from .Data import Data
import krakenex
from pykrakenapi import KrakenAPI


class KrakenData(Data):

    def __init__(self, interval=1, **params):
        self.KAPI = KrakenAPI(krakenex.API())
        self.ohlc, self.since = self.KAPI.get_ohlc_data(
            "BTCUSD",
            interval=interval,
            since=None,
            ascending=True,
        )
        self.firstCall = True
        self.interval = interval
        super().__init__(**params)

    def dataGenerator(self):
        wait = 60
        maxRows = 2880
        blockSize = 1440
            
        for retry in range(10):
            if not self.firstCall:
                # await asyncio.sleep(interval*wait)
                time.sleep(self.interval*wait)
            else:
                self.firstCall = False

            try:
                ohlcnew, self.since = self.KAPI.get_ohlc_data(
                    "BTCUSD",
                    interval=self.interval,
                    since=self.since,
                    ascending=True,
                )
            except (TimeoutError, ConnectionError):
                # await asyncio.sleep(wait)
                time.sleep(wait)
                retry += 1
                continue
            # Remove the last enty as it is unconfirmed
            retry = 0
            self.ohlc.drop(self.ohlc.tail(1).index, inplace=True)
            self.ohlc = self.ohlc.append(ohlcnew)
            if len(self.ohlc) >= maxRows:
                self.ohlc.drop(self.ohlc.head(blockSize).index,
                               inplace=True)
            yield self.ohlc
