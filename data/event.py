from decimal import Decimal
from enum import Enum
from pandas import Timestamp
from time import time


class TickType(Enum):
    TRADE   = 0
    QUOTE   = 1
    BAR     = 2
    FUNDING = 3

    
class EventType(Enum):
    TICK  = 0
    QUERY = 1
    RESPONSE = 2

    
class Event(object):
    """Base Event class for event-driven system"""
    @property
    def typename(self):
        return self.type.name

class QueryEvent(Event):
    """ Events placed on event queue will query respective api """
    def __init__(self, query_id, url):
        self.event_type = EventType.QUERY
        self.query_id   = query_id
        self.url        = url

    def __str__(self):
        return  f"{self.event_type} " \
                f"{self.query_id} " \
                f"{self.url}"

class ResponseEvent(Event):
    def __init__(self, query_id, http_response):
        self.event_type     = EventType.RESPONSE
        self.query_id       = query_id
        self.http_response  = http_response

    def __str__(self):
        return  f"{self.event_type} " \
                f"{self.query_id} " \
                f"{self.http_response}"


class QuoteEvent(Event):
    def __init__(self, exchange, pair, data):
        """ example data:
        {'timestamp': 1594266197.777497, 
         'receipt_timestamp': 1594266197.777497, 
         'delta': False, 
         'bid': {'9384.66': 2.656085}, 
         'ask': {'9384.67': 0.17725493}}
        """
        self.event_type        = EventType.TICK
        self.tick_type         = TickType.QUOTE
        self.exchange          = exchange
        self.pair              = pair
        self.full_name         = f"{exchange}-{pair}"
        self.timestamp         = data['timestamp']
        self.receipt_timestamp = data['receipt_timestamp']
        self.ask_price         = next(iter(data['ask'])) if data['ask'] else 0
        self.bid_price         = next(iter(data['bid'])) if data['bid'] else 0
        self.ask_size          = data['ask'][self.ask_price] if self.ask_price else 0
        self.bid_size          = data['bid'][self.bid_price] if self.bid_price else 0

    def __str__(self):
        return  f"{self.event_type} " \
                f"{self.tick_type} " \
                f"timestamp={self.timestamp} " \
                f"receipt timestamp={self.receipt_timestamp} " \
                f"exchange={self.exchange} " \
                f"pair={self.pair} " \
                f"bidprice={self.bid_price} " \
                f"askprice={self.ask_price} " \
                f"bidsize={self.bid_size} " \
                f"asksize={self.ask_size}"



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
            print(f"ERROR on TradeEvent. Data={data}. {e}")

    def __str__(self):
        return  f"{self.event_type} " \
                f"{self.tick_type} " \
                f"timestamp={self.timestamp} " \
                f"instrument={self.instrument} " \
                f"exchange={self.exchange} " \
                f"price={self.price} " \
                f"size={self.size} " \
                f"trade_id={self.trade_id}"


