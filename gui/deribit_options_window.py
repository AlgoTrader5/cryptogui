import sys
from decimal import Decimal
from PyQt5 import QtCore, QtWidgets, QtGui


import aiohttp
import asyncio
import websockets
import json
import time


class DeribitOptionsWindow(QtWidgets.QWidget):
    def __init__(self, events_engine, parent=None):
        super(DeribitOptionsWindow, self).__init__(parent)
        self.events_engine = events_engine
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_instruments())

        self.init_central_area()
        
        print("here!")


    def init_central_area(self):
        layout = QtWidgets.QHBoxLayout()
        update_btn = QtWidgets.QPushButton("Update")
        update_btn.clicked.connect(self.on_update_clicked)
        layout.addWidget(update_btn)
        self.setLayout(layout)

    async def fetch_tickers(self, session, url):
        params = None
        async with session.get(url=url, params=params) as response:
            http_response = await response.text()
            http_response = json.loads(http_response)
            return http_response

    async def init_instruments(self):
        self.instruments = {}
        urls = [
            "https://test.deribit.com/api/v2/public/get_instruments?currency=BTC&expired=false&kind=option",
            "https://test.deribit.com/api/v2/public/get_instruments?currency=ETH&expired=false&kind=option",
        ]
        tasks = []
        async with aiohttp.ClientSession() as session:
            for url in urls:
                print(url)
                tasks.append(self.fetch_tickers(session, url))
            ref_data = await asyncio.gather(*tasks, return_exceptions=True)
            for base_currency_options in ref_data:
                for option in base_currency_options['result']:
                    self.instruments[option['instrument_name']] = option
        print(f"Loaded {len(self.instruments)} Deribit options.")


    def on_update_clicked(self):
        print("Update button clicked!")



    

