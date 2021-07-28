from collections import namedtuple


Order = namedtuple('Order', [
    'Type',
    'Limit',
    'Quantity',
    'Leverage',
    'Stoploss',
    'Takeprofit',
    'Parent',
    'Strategy',
])
