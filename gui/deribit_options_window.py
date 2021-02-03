import sys
from decimal import Decimal
from PyQt5 import QtCore, QtWidgets, QtGui
from pprint import pprint

import aiohttp
import asyncio
import websockets
import json
import time

SOURCE_DIR = "D:/repos/cryptogui/data"
sys.path.append(SOURCE_DIR)
from event import QueryEvent


class DeribitOptionsWindow(QtWidgets.QWidget):
    ticker_signal = QtCore.pyqtSignal(object)

    def __init__(self, events_engine, parent=None):
        super(DeribitOptionsWindow, self).__init__(parent)
        self.events_engine = events_engine
        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.init_instruments())

        self.init_central_area()

        self.ticker_signal.connect(self.update_ticker)
        print("DeribitOptionsWindow")

    def update_ticker(self, e):
        data = e.http_response['result']
        pprint(data)



    def init_central_area(self):
        layout = QtWidgets.QVBoxLayout()
        grid = QtWidgets.QGridLayout()
        
        # instrument drop down menu
        self.instrument_combo_box = QtWidgets.QComboBox(self)
        self.instrument_combo_box.addItems(list(self.instruments.keys()))
        self.instrument_combo_box.setEditable(True)
        grid.addWidget(self.instrument_combo_box, 1, 1)
        
        # update push button
        update_btn = QtWidgets.QPushButton("Update")
        update_btn.clicked.connect(self.on_update_clicked)
        grid.addWidget(update_btn, 2, 1)

        group_box = QtWidgets.QGroupBox()
        group_box.setLayout(grid)
        layout.addWidget(group_box)
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
                tasks.append(self.fetch_tickers(session, url))
            ref_data = await asyncio.gather(*tasks, return_exceptions=True)
            for base_currency_options in ref_data:
                for option in base_currency_options['result']:
                    self.instruments[option['instrument_name']] = option
        print(f"Loaded {len(self.instruments)} Deribit options.")


    def on_update_clicked(self):
        print("Update button clicked!")
        instrument_str =  str(self.instrument_combo_box.currentText())
        query_str = f"https://test.deribit.com/api/v2/public/ticker?instrument_name={instrument_str}"
        self.events_engine.put(QueryEvent("DERIBIT_OPTIONS", query_str))



    

