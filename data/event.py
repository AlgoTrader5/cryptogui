from decimal import Decimal
from enum import Enum
from pandas import Timestamp
from time import time


class TickType(Enum):
    TRADE = 0
    QUOTE = 1
    BAR   = 2

class EventType(Enum):
    TICK  = 0

class Event(object):
    """Base Event class for event-driven system"""
    @property
    def typename(self):
        return self.type.name


class QuoteEvent(Event):
    def __init__(self, exchange, instrument, data):
        """ example data:
        {'timestamp': 1594266197.777497, 
         'receipt_timestamp': 1594266197.777497, 
         'delta': False, 
         'bid': {'9384.66': 2.656085}, 
         'ask': {'9384.67': 0.17725493}}
        """
        self.event_type        = EventType.TICK
        self.tick_type         = TickType.QUOTE
        self.timestamp         = data['timestamp']
        self.receipt_timestamp = data['receipt_timestamp']
        self.exchange          = exchange
        self.instrument        = instrument
        self.full_name         = f"{exchange}-{instrument}"
        self.ask_price         = next(iter(data['ask']))
        self.bid_price         = next(iter(data['bid']))
        self.ask_size          = data['ask'][self.ask_price]
        self.bid_size          = data['bid'][self.bid_price]



class TradeEvent(Event):
    def __init__(self, data):
        self.event_type = EventType.TICK
        self.tick_type  = TickType.TRADE
        try:
            self.timestamp  = data['timestamp']
            self.exchange   = data['feed']
            self.instrument = data['pair']
            self.full_name  = f"{self.exchange}-{self.instrument}"
            self.price      = data['price']
            self.size       = data['amount']
            self.side       = data['side']
            self.trade_id   = data['id'] if 'id' in data else None
        except KeyError as e:
            print(f"ERROR KEYING {data}. {e}")


    def __str__(self):
        return  f"{self.event_type} " \
                f"{self.tick_type} " \
                f"timestamp={self.timestamp} " \
                f"instrument={self.instrument} " \
                f"exchange={self.exchange} " \
                f"price={self.price} " \
                f"size={self.size} " \
                f"trade_id={self.trade_id}"

