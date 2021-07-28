import asyncio
import time
from .Data import Data
import krakenex
from pykrakenapi import KrakenAPI


class KrakenData(Data):

    def __init__(self, interval=1, waitInterval=1, **params):
        self.KAPI = KrakenAPI(krakenex.API())
        self.ohlc, self.since = self.KAPI.get_ohlc_data(
            "BTCUSD",
            interval=interval,
            since=None,
            ascending=True,
        )
        self.interval = interval
        self.waitInterval = waitInterval
        super().__init__(**params)

    async def dataGenerator(self):
        wait = 60
        maxRows = 2880
        blockSize = 1440
        retry = 0
        timer = None
        while retry < 10:
            if timer is not None:
                await timer
            try:
                ohlcnew, self.since = self.KAPI.get_ohlc_data(
                    "BTCUSD",
                    interval=self.interval,
                    since=self.since,
                    ascending=True,
                )
            except Exception:
                await asyncio.sleep(wait)
                retry += 1
                continue
            # Remove the last enty as it is unconfirmed
            retry = 0
            self.ohlc.drop(self.ohlc.tail(1).index, inplace=True)
            self.ohlc = self.ohlc.append(ohlcnew)
            if len(self.ohlc) >= maxRows:
                self.ohlc.drop(self.ohlc.head(blockSize).index,
                               inplace=True)
            timer = asyncio.create_task(asyncio.sleep(self.waitInterval*wait))
            yield self.ohlc
        raise ConnectionError("Retry Exceeded 10")
