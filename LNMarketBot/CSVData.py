from .Data import Data
import pandas
import datetime as dt


class CSVData(Data):

    def __init__(
            self,
            filename,
            window,
            datetime='datetime',
            volume='volume',
            open_='open',
            high='high',
            low='low',
            close='close',
            start=None,
            end=None,
            interval=60,
            **params,
    ):
        fileData = pandas.read_csv(filename)
        # convert the column (it's a string) to datetime type
        datetime_series = pandas.to_datetime(fileData[datetime])

        # create datetime index passing the datetime series
        datetime_index = pandas.DatetimeIndex(datetime_series.values)
        fileData = fileData.set_index(datetime_index)
        fileData.drop(datetime, axis=1, inplace=True)
        self.ohlc = fileData.rename(columns={
            open_: 'open',
            high: 'high',
            low: 'low',
            close: 'close',
            volume: 'volume',
        })
        self.window = window
        self.interval = interval
        if end is None:
            self.start = fileData.index[0] + self.window
            self.end = fileData.index[-1]
        else:
            self.start = start
            assert(end is not None)
            self.end = end
        super().__init__(**params)

    def dataGenerator(self):
        for seconds in range(0, round((self.end-self.start).total_seconds()),
                             self.interval):
            end = self.start+dt.timedelta(seconds=seconds)
            start = end-self.window
            yield self.ohlc[start:end]
