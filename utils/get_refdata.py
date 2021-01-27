import aiohttp
import argparse
import asyncio
import json

from pprint import pprint
from tabulate import tabulate

def get_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--coinbase",  action='store_true', default=False)
    parser.add_argument("--deribit",   action='store_true', default=False)
    parser.add_argument("--binanceus", action='store_true', default=False)
    parser.add_argument("--ftxus",     action='store_true', default=False)
    parser.add_argument("--spot-only", dest='spot_only', action='store_true', default=False)
    parser.add_argument("--futures-only", dest='futures_only', action='store_true', default=False)
    parser.add_argument("--options-only", dest='options_only', action='store_true', default=False)
    parser.add_argument("--names-only", dest='names_only', action='store_true', default=False)

    return parser.parse_args()



class DeribitRefData:
    def __init__(self):
        self.name = "Deribit"
        # self.url = "https://test.deribit.com/api/v2/public/get_instruments?currency=BTC&expired=false&kind=option"
        # self.url = "https://test.deribit.com/api/v2/public/get_instruments?currency=ETH&expired=false&kind=option"
        # self.url = "https://test.deribit.com/api/v2/public/get_instruments?currency=USDT&expired=false&kind=option"
        # self.url = "https://test.deribit.com/api/v2/public/get_instruments?currency=BTC&expired=false&kind=future"
        self.url = "https://test.deribit.com/api/v2/public/get_instruments?currency=ETH&expired=false&kind=future"
        # self.url = "https://test.deribit.com/api/v2/public/get_instruments?currency=USDT&expired=false&kind=future"
        
        self.params = None


    def parse(self, data):
        '''
             {'base_currency': 'BTC',
              'block_trade_commission': 0.00015,
              'contract_size': 1.0,
              'creation_timestamp': 1605267263000,
              'expiration_timestamp': 1611907200000,
              'instrument_name': 'BTC-29JAN21-14000-P',
              'is_active': True,
              'kind': 'option',
              'maker_commission': 0.0003,
              'min_trade_amount': 0.1,
              'option_type': 'put',
              'quote_currency': 'USD',
              'settlement_period': 'month',
              'strike': 14000.0,
              'taker_commission': 0.0003,
              'tick_size': 0.0005}
        '''
        results = []
        keys_to_remove = []
        for ticker in data['result']:
            # for k in keys_to_remove:
            #     ticker.pop(k)
            results.append(ticker)
        return {self.name: results}

class CoinbaseRefData:
    def __init__(self):
        self.name = "Coinbase"
        self.url = "https://api.pro.coinbase.com/products"
        self.params = None

    def parse(self, data):
        ''' [{'id': 'XTZ-GBP', 'base_currency': 'XTZ', 'quote_currency': 'GBP', 
              'base_min_size': '1.00000000', 'base_max_size': '100000.00000000', 
              'quote_increment': '0.00001000', 'base_increment': '0.01000000', 
              'display_name': 'XTZ/GBP', 'min_market_funds': '10', 
              'max_market_funds': '100000', 'margin_enabled': False, 
              'post_only': False, 'limit_only': False, 'cancel_only': False, 
              'trading_disabled': False, 'status': 'online', 'status_message': ''},
        '''
        results = []
        keys_to_remove = ['margin_enabled','status_message','post_only','cancel_only','status',
                          'max_market_funds','min_market_funds','limit_only','trading_disabled']
        for ticker in data:
            for k in keys_to_remove:
                ticker.pop(k)
            results.append(ticker)
        return {self.name: results}


class FTXUSRefData:
    def __init__(self):
        self.name = "FTXUS"
        self.url = "https://ftx.us/api/markets"
        self.params = None

    def parse(self, data: dict) -> dict:
        ''' {'result': [{'ask': 311.4, 'baseCurrency': 'BCH', 'bid': 311.1, 
                         'change1h': 0.005245742877895246, 'change24h': 0.06416061512174284, 
                         'changeBod': 0.0376541152949017, 'enabled': True, 
                         'highLeverageFeeExempt': True, 'last': 311.625, 
                         'minProvideSize': 0.001, 'name': 'BCH/USD', 'postOnly': False, 
                         'price': 311.4, 'priceIncrement': 0.025, 'quoteCurrency': 'USD', 
                         'quoteVolume24h': 566793.070825, 'restricted': False, 
                         'sizeIncrement': 0.001, 'type': 'spot', 'underlying': None, 
                         'volumeUsd24h': 566793.070825}, ... ],
             'success': True}

        returns:
            {'baseCurrency': 'BCH',
             'minProvideSize': 0.001,
             'name': 'BCH/USDT',
             'postOnly': False,
             'priceIncrement': 0.025,
             'quoteCurrency': 'USDT',
             'restricted': False,
             'sizeIncrement': 0.001,
             'type': 'spot',
             'underlying': None}


        '''
        results = []
        keys_to_remove = ['ask', 'bid', 'change1h', 'change24h', 'changeBod', 'enabled',
                          'highLeverageFeeExempt', 'last', 'price','quoteVolume24h',
                          'volumeUsd24h','restricted','postOnly'
        ]
        for symbol in data['result']:
            for k in keys_to_remove:
                symbol.pop(k)
            results.append(symbol)
        return {self.name: results}


class BinanceUSRefData:
    def __init__(self):
        self.name = "BinanceUS"
        self.url = "https://api.binance.us/api/v3/exchangeInfo"
        self.params = None

    def parse(self, data: dict):
        '''
        dict_keys(['timezone', 'serverTime', 'rateLimits', 'exchangeFilters', 'symbols'])
         'filters': [{'filterType': 'PRICE_FILTER',
                                     'maxPrice': '10000.0000',
                                     'minPrice': '0.0010',
                                     'tickSize': '0.0010'},
                                    {'avgPriceMins': 5,
                                     'filterType': 'PERCENT_PRICE',
                                     'multiplierDown': '0.2',
                                     'multiplierUp': '5'},
                                    {'filterType': 'LOT_SIZE',
                                     'maxQty': '900000.00000000',
                                     'minQty': '0.00100000',
                                     'stepSize': '0.00100000'},
                                    {'applyToMarket': True,
                                     'avgPriceMins': 5,
                                     'filterType': 'MIN_NOTIONAL',
                                     'minNotional': '10.0000'},
                                    {'filterType': 'ICEBERG_PARTS', 'limit': 10},
                                    {'filterType': 'MARKET_LOT_SIZE',
                                     'maxQty': '6802.60544892',
                                     'minQty': '0.00000000',
                                     'stepSize': '0.00000000'},
                                    {'filterType': 'MAX_NUM_ALGO_ORDERS',
                                     'maxNumAlgoOrders': 5},
                                    {'filterType': 'MAX_NUM_ORDERS',
                                     'maxNumOrders': 200}]
        '''
        results = []
        keys_to_remove = ['baseAssetPrecision','quoteAssetPrecision','quoteCommissionPrecision',
                          'baseCommissionPrecision','orderTypes','isMarginTradingAllowed',
                          'quotePrecision','status','isSpotTradingAllowed','ocoAllowed','icebergAllowed',
                          'quoteOrderQtyMarketAllowed']
        for ticker in data['symbols']:
            for k in keys_to_remove:
                ticker.pop(k)
            filters = ticker.pop('filters')
            for f in filters:
                if f['filterType'] in ['PRICE_FILTER','LOT_SIZE']:
                    if 'tickSize' in f:
                        ticker['tickSize'] = f['tickSize']
                    if 'minQty' in f:
                        ticker['minQty'] = f['minQty']
                    if 'maxQty' in f:
                        ticker['maxQty'] = f['maxQty']
            results.append(ticker)
        return {self.name: results}


async def fetch_tickers(session, url_object):
    url = url_object.url
    params = url_object.params
    async with session.get(url=url, params=params) as response:
        http_response = await response.text()
        http_response = json.loads(http_response)
        http_response = url_object.parse(http_response)
        return http_response

async def main():
    args = get_args()

    urls = []
    if args.coinbase:
        urls.append(CoinbaseRefData())
    if args.binanceus:
        urls.append(BinanceUSRefData())
    if args.ftxus:
        urls.append(FTXUSRefData())
    if args.deribit:
        urls.append(DeribitRefData())

    if len(urls) == 0:
        print("Grabbing ALL refdata.")
        urls = [
            CoinbaseRefData(),
            FTXUSRefData(),
            BinanceUSRefData(),
            DeribitRefData()
        ]
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch_tickers(session, url))
        ref_data = await asyncio.gather(*tasks, return_exceptions=True)
        for i in ref_data:
            for k,v in i.items():
                for data in v:
                    # if args.names_only:
                    #     print(data[''])
                    print(data)




if __name__ == '__main__':
    loop = asyncio.get_event_loop().run_until_complete(main())
