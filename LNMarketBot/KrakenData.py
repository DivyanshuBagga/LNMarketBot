import asyncio
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
        super().__init__(interval=interval, **params)

        def dataGenerator(self):
            assert(self.liveTrading)
            wait = 60
            maxRows = 2880
            blockSize = 1440
            if not self.firstCall:
                await asyncio.sleep(interval*wait)
            else:
                self.firstCall = False

            for retry in range(10):
                try:
                    ohlcnew, self.since = self.KAPI.get_ohlc_data(
                        "BTCUSD",
                        interval=interval,
                        since=self.since,
                        ascending=True,
                    )
                except [TimeoutError, ConnectionError]:
                    await asyncio.sleep(wait)
                    retry += 1
                    continue
                # Remove the last enty as it is unconfirmed
                self.ohlc.drop(self.ohlc.tail(1).index, inplace=True)
                self.ohlc = self.ohlc.append(ohlcnew)
                if len(self.ohlc) >= maxRows:
                    self.ohlc.drop(self.ohlc.head(blockSize).index,
                                   inplace=True)
                    yield self.ohlc
